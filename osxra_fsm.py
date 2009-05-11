#!/usr/bin/env python
import time
import random
import commands
import platform

from fsm import FSM

STATES = ["UNINITIALIZED", "INITIALIZED", "ACTIVE", "INACTIVE" "ERROR"]
#could be called "INPUT_EVENTS":
ACTIONS = ["GET_VOLUME", "SET_VOLUME"]

"""
Plan:
    Put volume levels into FSM memory
"""


class Volume(object):
    """Object representation of a system's volume"""

    def __init__(self, set_cmd=None, get_cmd=None, contract=None):
        self._platform = platform.system()
        if self._platform == "Darwin": #OSX
            if set_cmd is None:
                self.set_cmd = "osascript -e 'set volume output volume %d'"
            if get_cmd is None:
                self.get_cmd = "osascript -e 'set V to output volume of (get volume settings)'"
            if contract is None:
                self.contract = {"type":int, "range":range(0, 101)}
        elif self._platform == "Linux":
            raise NotImplementedError #TODO - use 'festival' command
        else:
            raise RuntimeError, "'%s' platform not supported" % self._platform

    def get_volume(self):
        """Get current Volume value.
        """
        value = commands.getoutput(self.get_cmd)
        value = self._check_value_with_contract(value)
        if isinstance(value, self.contract["type"]):
            return value
        else:
            raise ValueError, value

    def set_volume(self, value, cmd=None, contract_range=None):
        """Set Volume's value.
        """
        value = self._check_value_with_contract(value)
        if isinstance(value, self.contract["type"]):
            result = commands.getoutput(self.set_cmd % value)
            return
        else:
            raise ValueError, value

    value = property(get_volume, set_volume) #set getter & and setter

    def _check_value_with_contract(self, value):
        contract_type = self.contract["type"]
        contract_range = self.contract["range"]
        try:
            value = contract_type(value)
        except ValueError, e:
            return {"ERROR":e}
        if value not in contract_range:
            return {"ERROR":"volume not in contract_range"}
        return value



