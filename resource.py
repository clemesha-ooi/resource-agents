#!/usr/bin/env python
import sys
sys.path.append("../magnet")

from twisted.application import service, internet
from twisted.web import resource, server
from twisted.internet import reactor
from magnet import pole
from magnet import field

from agents import ResourceAgent

HOST = "amoeba.ucsd.edu"
SPEC = "../magnet/magnet/spec/amqp0-8.xml"


VH = "/" #vhost
X = "webservers" #exchange
RP = "*" #routing_pattern
SYS = "resource_agents" #system_name
SER = "resource" #service_name 
T = "nginx-controller" #token

class ResourceWebUI(resource.Resource):

    def __init__(self, service):
        resource.Resource.__init__(self)
        self.service = service

    def getChild(self, name, request):
        if name == '':
            return self
        return resource.Resource.getChild(self, name, request)

    def render_GET(self, request):
        #print self.service.__dict__
        msg = request.args.get("msg", ["ResourceWebUI accessed"])[0]
        print "Sending msg => '%s'" % msg
        msgobj = {"method":"hello", "payload":msg}
        self.service.sendMessage(msgobj, "webui")
        return "ResourceWebUI  sent '%s'" % msg



agent = ResourceAgent(exchange=X, routing_pattern=RP, system_name=SYS, service_name=SER, token=T)
c = field.IAMQPClient(agent)
connector = field.AMQPClientConnectorService(reactor, c)
connector.connect(host=HOST, vhost=VH, spec_path=SPEC)
#vhost=VH, 

webui = ResourceWebUI(connector)
webuisite = internet.TCPServer(8009, server.Site(webui))

application = service.Application("controller")

webuisite.setServiceParent(application) 
connector.setServiceParent(application)
