#!/usr/bin/env python
import os
import sys
sys.path.append("../magnet")
from magnet import pole
from magnet import field

from string import Template

from twisted.application import service, internet
from twisted.web import resource, server, static
from twisted.internet import reactor

from agents import ResourceAgent, ControllerAgent

HOST = "amoeba.ucsd.edu"
SPEC = "../magnet/magnet/spec/amqp0-8.xml"


VH = "/resource_agents" #vhost
X = "webservers" #exchange
RP = "*" #routing_pattern
SYS = "resource_agents" #system_name
SER = "resource" #service_name 
r_T = "nginx_resource_agent" #token
c_T = "controller_agent" #token

class ResourceWebUI(resource.Resource):

    def __init__(self, service):
        resource.Resource.__init__(self)
        self.service = service

    def getChild(self, name, request):
        if name == '':
            return self
        return resource.Resource.getChild(self, name, request)

    def render_GET(self, request):
        method = request.args.get("method", ["hello"])[0]
        action = request.args.get("action", ["INIT"])[0]
        action = action.upper()

        payload = {"from":self.__class__.__name__, "action":action}
        msgobj = {"method":method, "payload":payload}
        #print "Sending msg => '%s'" % msgobj
        self.service.sendMessage(msgobj, "webui")
        return "Action=> %s " % action

class ControllerWebUI(resource.Resource):

    def __init__(self, service):
        resource.Resource.__init__(self)
        self.service = service

    def getChild(self, name, request):
        if name == '':
            return self
        return resource.Resource.getChild(self, name, request)

    def render_GET(self, request):
        method = request.args.get("method", ["hello"])[0]
        action = request.args.get("action", ["INIT"])[0]
        action = action.upper()

        payload = {"from":self.__class__.__name__, "action":action}
        msgobj = {"method":method, "payload":payload}
        #print "Sending msg => '%s'" % msgobj
        self.service.sendMessage(msgobj, "webui")
        return "Action=> %s " % action

class Root(resource.Resource):
    isLeaf = False

    def getChild(self, name, request):
        if name == '':
            return self
        return resource.Resource.getChild(self, name, request)

    def render_GET(self, request):
        tvals = {}
        html = Template(open("static/index.html").read()).substitute(tvals)
        return html



# === Agents ===
r_agent = ResourceAgent(exchange=X, routing_pattern=RP, system_name=SYS, service_name=SER, token=r_T)
r_connector = field.AMQPClientConnectorService(reactor, field.IAMQPClient(r_agent), name="r_agent")
r_connector.connect(host=HOST, vhost=VH, spec_path=SPEC)

c_agent = ControllerAgent(exchange=X, routing_pattern=RP, system_name=SYS, service_name=SER, token=c_T)
c_connector = field.AMQPClientConnectorService(reactor, field.IAMQPClient(c_agent), name="c_agent")
c_connector.connect(host=HOST, vhost=VH, spec_path=SPEC)
#================


# === Web Interface ===
webui = Root()
webui.putChild('resource', ResourceWebUI(r_connector))
webui.putChild('controller', ControllerWebUI(c_connector))
webui.putChild('static', static.File(os.path.join(os.path.abspath("."), "static")))

webuisite = internet.TCPServer(8008, server.Site(webui))
#=======================


# === Twisted Application ===
application = service.Application("resource_agents")
webuisite.setServiceParent(application) 
r_connector.setServiceParent(application)
c_connector.setServiceParent(application)
