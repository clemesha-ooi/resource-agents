#!/usr/bin/env python
import sys
sys.path.append("../magnet")

from twisted.application import service, internet
from twisted.web import resource, server
from twisted.internet import reactor
from magnet import pole
from magnet import field

HOST = "amoeba.ucsd.edu"
SPEC = "../magnet/magnet/spec/amqp0-8.xml"


VH = "/" #vhost
X = "webservers" #exchange
RP = "nginx.config.change" #routing_pattern
SYS = "prototypes" #system_name
SER = "controller" #service_name 
T = "nginx-controller" #token

class ControllerAgent(pole.BasePole):

    def do_when_running(self):
        print "=== %s running ===" % self.__class__.__name__
        print dir(self)

class ControllerWebUI(resource.Resource):

    def __init__(self, service):
        resource.Resource.__init__(self)
        self.service = service

    def getChild(self, name, request):
        if name == '':
            return self
        return resource.Resource.getChild(self, name, request)

    def render_GET(self, request):
        #print self.service.__dict__
        msg = request.args.get("msg", ["ControllerWebUI accessed"])[0]
        print "Sending msg => '%s'" % msg
        self.service.sendMessage(msg, "webui")
        return "ControllerWebUI sent '%s'" % msg



agent = ControllerAgent(exchange=X, routing_pattern=RP, system_name=SYS, service_name=SER, token=T)
c = field.IAMQPClient(agent)
connector = field.AMQPClientConnectorService(reactor, c)
connector.connect(host=HOST, vhost=VH, spec_path=SPEC)
#vhost=VH, 

webui = ControllerWebUI(connector)
webuisite = internet.TCPServer(8008, server.Site(webui))

application = service.Application("controller")

webuisite.setServiceParent(application) 
connector.setServiceParent(application)
