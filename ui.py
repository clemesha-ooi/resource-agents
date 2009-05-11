#!/usr/bin/env python
import os
import sys
sys.path.append("../magnet")
from magnet import pole
from magnet import field

from string import Template
import simplejson as json

from twisted.application import service, internet
from twisted.web import resource, server, static
from twisted.internet import reactor

from agent_roles import Say, Disk

HOST = "amoeba.ucsd.edu"
SPEC = "../magnet/magnet/spec/amqp0-8.xml"


VH = "/resource_agents" #vhost
X = "ui" #exchange
RP = "*" #routing_pattern
SYS = "resource_agents" #system_name
SER = "resource" #service_name 
r_T = "nginx_resource_agent" #token
c_T = "controller_agent" #token

class ResourceAgentUI(resource.Resource):

    def __init__(self, service):
        resource.Resource.__init__(self)
        self.service = service

    def getChild(self, name, request):
        if name == '':
            return self
        return resource.Resource.getChild(self, name, request)

    def render_GET(self, request):
        role = request.args.get("role", ["Control"])[0]
        method = request.args.get("method", ["say"])[0]
        payload = request.args.get("payload", ["hello world"])[0]

        role_payload = {"from":self.__class__.__name__, "method":method, "payload":payload}
        msgobj = {"role":role, "payload":role_payload}
        #print "Sending msg => '%s'" % msgobj
        self.service.consume_message(msgobj)
        return "{'method':%s, 'payload':%s}" % (method, payload)

class ControllerAgentUI(resource.Resource):

    def __init__(self, service):
        resource.Resource.__init__(self)
        self.service = service

    def getChild(self, name, request):
        if name == '':
            return self
        return resource.Resource.getChild(self, name, request)

    def render_GET(self, request):
        role = request.args.get("role", ["Control"])[0]
        method = request.args.get("method", ["say"])[0]
        payload = request.args.get("payload", ["hello world"])[0]

        role_payload = {"from":self.__class__.__name__, "method":method, "payload":payload}
        msgobj = {"role":role, "payload":role_payload}
        #print "Sending msg => '%s'" % msgobj
        self.service.consume_message(msgobj)
        return "{'method':%s, 'payload':%s}" % (method, payload)

class Root(resource.Resource):
    isLeaf = False

    def getChild(self, name, request):
        if name == '':
            return self
        return resource.Resource.getChild(self, name, request)

    def _get_children_info(self):
        """Get listing of all children and their associated 
        urls and class names.

        This where we can expose all Agent's entry points 
        from the UI (aka 'what Agents do we have, and what 
        are their methods?')
        """
        children_info = {}
        #XXX use "twisted.python.reflect" or Python's inspect model here:
        for kv in self.children.iteritems():
            try:
                # if a child has attr 'service', we assume it has 
                # a corresponding Agent and url. #XXX inspect all methods as well.
                if hasattr(kv[1], "service"):
                    #kv[1].service.amqpclient #get other data from here: exchange, rk, etc
                    #print dir(kv[1].service)
                    #print dir(kv[1].service.connector)

                    # children_info[url] = Agents UI class name
                    children_info[kv[0]] = kv[1].__class__.__name__
            except AttributeError:
                continue
        return json.dumps(children_info)

    def render_GET(self, request):
        children_info = self._get_children_info()
        tvals = {"agents":children_info}
        html = Template(open("static/index.html").read()).substitute(tvals)
        return html


# --- new agent ----


say_role = Say('C')
disk_role = Disk('M')

r_agent = pole.Agent(X, "osx") #(exchange, resource)
r_agent.addRole(say_role)
r_agent.addRole(disk_role)
r_manlay = field.ChannelManagementLayer()
r_manlay.addAgent(r_agent)
r_connector = field.AMQPConnector(r_manlay, host='amoeba.ucsd.edu', spec_path=SPEC)
r_connector.connect()

c_agent = pole.Agent(X, "osx") #(exchange, resource)
c_agent.addRole(say_role)
c_agent.addRole(disk_role)
c_manlay = field.ChannelManagementLayer()
c_manlay.addAgent(c_agent)
c_connector = field.AMQPConnector(c_manlay, host='amoeba.ucsd.edu', spec_path=SPEC)
c_connector.connect()


# === Web Interface ===
webui = Root()
webui.putChild('resource', ResourceAgentUI(r_agent))
webui.putChild('controller', ControllerAgentUI(c_agent))
webui.putChild('static', static.File(os.path.join(os.path.abspath("."), "static")))

webuisite = internet.TCPServer(8008, server.Site(webui))
#=======================


# === Twisted Application ===
application = service.Application("resource_agents")
webuisite.setServiceParent(application) 
r_connector.setServiceParent(application)
c_connector.setServiceParent(application)
