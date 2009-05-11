#!/usr/bin/env python

import platform

from twisted.internet.utils import getProcessOutput
from twisted.internet import defer, reactor
from twisted.python import log


class Volume(object):
    """Object representation of a system's volume"""

    def __init__(self, set_cmd=None, get_cmd=None, contract=None):
        self._platform = platform.system()
        if self._platform == "Darwin": #OSX
            if set_cmd is None:
                self.set_cmd = "/usr/bin/osascript"
                self.set_cmdflag, self.set_cmdval = "-e", "set volume output volume %d"
            if get_cmd is None:
                self.get_cmd = "/usr/bin/osascript"
                self.get_cmdflag, self.get_cmdval = "-e", "set V to output volume of (get volume settings)"
            if contract is None:
                self.contract = {"type":int, "range":range(0, 101)}
        elif self._platform == "Linux":
            raise NotImplementedError #TODO 
        else:
            raise RuntimeError, "'%s' platform not supported" % self._platform

    @defer.inlineCallbacks
    def get_volume(self):
        """Get current Volume value.
        """
        value = yield getProcessOutput(self.get_cmd, [self.get_cmdflag, self.get_cmdval])
        value = self._check_value_with_contract(value)
        if isinstance(value, self.contract["type"]):
            defer.returnValue(value)
        else:
            raise ValueError, value

    @defer.inlineCallbacks
    def set_volume(self, value, cmd=None, contract_range=None):
        """Set Volume's value.
        """
        value = self._check_value_with_contract(value)
        if isinstance(value, self.contract["type"]):
            result = yield getProcessOutput(self.set_cmd, [self.set_cmdflag, self.set_cmdval % value])
            defer.returnValue(value)
        else:
            raise ValueError, value

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


@defer.inlineCallbacks
def say(args):
    result = yield getProcessOutput("/usr/bin/say", [args])


@defer.inlineCallbacks
def disk_space(args=["-g", "/"]):
    result = yield getProcessOutput("/bin/df", args)
    vals = []
    for e in result.split("\n")[1].split(" "):
        try:
            vals.append(int(e))
        except ValueError:
            continue
    blocks, used, avail = vals
    print blocks, used, avail
    defer.returnValue([used, avail])


if __name__ == "__main__":

    @defer.inlineCallbacks
    def say_disk_info():
        #used, avail = disk_space()
        used, avail = yield disk_space()
        #used, avail = 100, 20
        say("This resource has %d megabytes free disk, and %d used." % (avail, used))

    reactor.callLater(2, say_disk_info)
    reactor.callLater(4, reactor.stop)
    reactor.run()

    """
    volume = Volume()
    def gsv(val):
        "get set volume"
        v = volume.get_volume()
        def p(x):
            print "volume => ", x
        v.addCallback(p)
        def sv(_, val):
            print "setting val ", val
            volume.set_volume(val)
        v.addCallback(sv, val)

    reactor.callLater(1, say, ["hello world"])
    reactor.callLater(2, gsv, "40")
    reactor.callLater(4, reactor.stop)
    reactor.run()
    """

