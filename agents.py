import sys
sys.path.append("../magnet")
from magnet import pole
from magnet import field

from twisted.internet import task


class BaseFSMAgent(pole.BasePole):
    """An Agent that manages it's state with a Finite State Machine.
    
    """
    def __init__(self, check_time=3, exchange='magnet', routing_pattern='test', system_name='test', service_name='test', token=None):
        pole.BasePole.__init__(self, exchange, routing_pattern, system_name, service_name, token)
        self.state = []
        updatestate = task.LoopingCall(self.update_state)
        updatestate.start(check_time) #check state stack every check_time seconds

    def do_when_running(self):
        print "=== %s running ===" % self.__class__.__name__
    
    def update_state(self): 
        """Pop actions off the state stack and
        pass them to this Agent's FSM to be handled.
        """
        print "updating state..."
        while self.state:
            print "Pop state value => ", self.state.pop()


class ControllerAgent(BaseFSMAgent):
    def action_hello(self, msg):
        self.state.append(msg)
        print "= In class: %s === msg: %s" % (self.__class__.__name__, msg)

class ResourceAgent(BaseFSMAgent):
    def action_hello(self, msg):
        self.state.append(msg)
        print "= In class: %s === msg: %s" % (self.__class__.__name__, msg)



