"""
controller and supervisor

keep track of things (agents/resources)

listen for agents to come online
agents register here
controller replys with heartbeat rate

Hello Message:
    role: agent control
    agent id:id
    payload:register me

    Response:
    role: agent control
    
    payload:register-ok
            heartbeat=3

"""
import os
import sys

from twisted.python import log
from twisted.internet import reactor

log.startLogging(sys.stdout)

from magnet import pole
from magnet import field

import magnet
spec_path_def = os.path.join(magnet.__path__[0], 'spec', 'amqp0-8.xml')

EXCHANGE = 'agents'
RESOURCE = 'Controller'

class ManagedAgent(object):
    name = None
    id = None
    last_heartbeat = None

    def __init__(self, name, id):
        self.name = name
        self.id = id

    def touch(self):
        """touch heartbeat timestamp
        """
        self.last_heartbeat = time.time()


class AgentController(pole.Role):

    registry = {}
    heartbeat = 3
    name = 'Agent Control'

    def action_register(self, message_object):
        """
        resource_agent = resource_name:agent_unique_id
        """
        agent_id = message_object['agent_id']
        agent_name = message_object['agent_name']
        agent = self.registry.get(agent_id, None)
        if agent is None:
            agent = ManagedAgent(agent_name, agent_id)
        self.registry[agent_id] = agent
        self.agent.known_agents[agent_id] = (self.agent.exchange, agent_id,)
        self.register_ok(agent_id)

    def register_ok(self, agent_id):
        payload = {'method':'register_ok',
                    'payload':self.heartbeat}
        self.sendMessage(agent_id, payload) 

    def action_heartbeat(self, message_object):
        agent_id = message_object['agent_id']

    def action_disk_usage(self, message_object):
        agent = self.registry.get(message_object['agent_id'])
        agent.set_diskusage(message_object['payload'])


agent_controller = AgentController()

controller_agent = pole.Agent(EXCHANGE, RESOURCE)
controller_agent.addRole(agent_controller)

ams = field.ChannelManagementLayer()
ams.addAgent(controller_agent)
amqpConnector = field.AMQPConnector(ams, host='amoeba.ucsd.edu',
        spec_path=spec_path_def)

amqpConnector.connect()
reactor.run()
