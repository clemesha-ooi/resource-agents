import sys
sys.path.append("../magnet")
from magnet import pole
from magnet import field

from twisted.internet import task

from agent_fsm import create_new_fsm

class BaseFSMAgent(pole.BasePole):
    """An Agent that manages it's state with a Finite State Machine.

    An Agent has a 'state' stack that queues incoming messages 
    that are destined to be passed to the Agent's FSM.
    (This may be closely related the Agent's 'memory', not sure yet)

    ? How to handle many messages in the 'state' stack, when passed to FSM.
    
    """
    def __init__(self, check_time=3, exchange='magnet', routing_pattern='test', system_name='test', service_name='test', token=None):
        pole.BasePole.__init__(self, exchange, routing_pattern, system_name, service_name, token)
        self.state = []
        self.fsm = create_new_fsm()
        updatestate = task.LoopingCall(self.update_state)
        updatestate.start(check_time) #check state stack every check_time seconds

    def do_when_running(self):
        """Where an Agent announces it's existence in the network?
        """
        print "=== %s running ===" % self.__class__.__name__
    
    def update_state(self): 
        """Pop actions off the state stack and
        pass them to this Agent's FSM to be handled.

        """
        print "updating '%s' ... state=%s" % (self.__class__.__name__, self.state)
        try:
            action = self.state.pop()
            print "pop action=>'%s'" % action
            self.fsm.process(action)
        except IndexError:
            pass #no action messages needed to be handled
        

class ControllerAgent(BaseFSMAgent):
    def action_hello(self, msg):
        action = msg["payload"]["action"]
        self.state.append(action)
        print "= In class: %s === msg: %s" % (self.__class__.__name__, msg)

class ResourceAgent(BaseFSMAgent):
    def action_hello(self, msg):
        action = msg["payload"]["action"]
        self.state.append(action)
        print "= In class: %s === msg: %s" % (self.__class__.__name__, msg)



