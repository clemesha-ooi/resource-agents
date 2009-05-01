#!/usr/bin/env python
import sys
sys.path.append("../magnet")
from magnet import pole
from magnet import field

from twisted.application import service, internet
from twisted.web import resource, server
from twisted.internet import reactor

from agents import ControllerAgent

HOST = "amoeba.ucsd.edu"
SPEC = "../magnet/magnet/spec/amqp0-8.xml"

VH = "/" #vhost
X = "webservers" #exchange
RP = "*" #routing_pattern
SYS = "resource_agents" #system_name
SER = "controller" #service_name 
T = "controller" #token

PORT = 8008

class ControllerWebUI(resource.Resource):

    def __init__(self, service):
        resource.Resource.__init__(self)
        self.service = service

    def getChild(self, name, request):
        if name == '':
            return self
        return resource.Resource.getChild(self, name, request)

    def render_GET(self, request):
        msg = request.args.get("msg", ["ControllerWebUI accessed"])[0]
        print "Sending msg => '%s'" % msg
        msgobj = {"method":"hello", "payload":msg}
        self.service.sendMessage(msgobj, "webui")
        return "ControllerWebUI sent '%s'" % msg


agent = ControllerAgent(exchange=X, routing_pattern=RP, system_name=SYS, service_name=SER, token=T)
c = field.IAMQPClient(agent)
connector = field.AMQPClientConnectorService(reactor, c)
connector.connect(host=HOST, vhost=VH, spec_path=SPEC)

webui = ControllerWebUI(connector)
webuisite = internet.TCPServer(PORT, server.Site(webui))

application = service.Application("controller")

webuisite.setServiceParent(application) 
connector.setServiceParent(application)
