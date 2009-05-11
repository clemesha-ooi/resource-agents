import os
import pwd
import sys
from twisted.internet.utils import getProcessOutput
from twisted.internet import defer
from twisted.python import log

sys.path.append("../magnet")
from magnet import pole
from magnet import field

from osx_resource import Volume, disk_space

VOICE = "Fred"

class Say(pole.ResourceCapability):
    """
    """
    def sendOK(self, result):
        reply = {'method': 'reply', 'payload': 'ok'}
        self.sendMessage("Controller", reply)

    def sendError(self, failure):
        reply = {'method': 'reply', 'payload': 'got an error running say'}
        self.sendMessage("Controller", reply)

    def action_say(self, message_object):
        to_say = message_object['payload']
        log.msg('Got say message: %s' % message_object['payload'])
        d = getProcessOutput('/usr/bin/say', ['-v', VOICE, to_say])
        d.addCallback(self.sendOK).addErrback(self.sendError)
        return None


class Disk(pole.ResourceMonitorRole):
    def sendOK(self, result):
        reply = {'method': 'reply', 'payload': 'ok'}
        self.sendMessage("Controller", reply)

    def sendError(self, failure):
        reply = {'method': 'reply', 'payload': 'got an error running Disk'}
        self.sendMessage("Controller", reply)

    @defer.inlineCallbacks
    def action_disk(self, message_object):
        used, avail = yield disk_space()
        name = pwd.getpwuid(os.getuid())[4].split(" ")[0] 
        say = "Hello %s.  Your resource has %d gigabytes free disk, and %d used." % (name, avail, used)
        result = yield getProcessOutput('/usr/bin/say', ['-v', VOICE, say])
        self.sendMessage("Controller", reply)

class DemoRole(pole.Role):
    name = "DemoRole"

    @defer.inlineCallbacks
    def action_disk(self, message_object):
        used, free = yield disk_space()
        name = pwd.getpwuid(os.getuid())[4].split(" ")[0] 
        say = "Hello %s.  Your resource has %d gigabytes free disk, and %d used." % (name, free, used)
        log.msg("action_disk - say:%s" % say)
        result = yield getProcessOutput('/usr/bin/say', ['-v', VOICE, say])
        reply = {'method': 'reply', 'free':free, 'used':used}
        self.sendMessage("Controller", reply)

    @defer.inlineCallbacks
    def action_set_volume(self, message_object):
        volume = Volume()
        value = message_object["payload"]
        result = yield volume.set_volume(value)
        log.msg("action_set_volume - result: %s" % result)
        reply = {'method': 'reply', 'payload': 'ok'}
        self.sendMessage("Controller", reply)

    @defer.inlineCallbacks
    def action_say(self, message_object):
        to_say = message_object['payload']
        log.msg('action_say - to_say: %s' % to_say)
        result = yield getProcessOutput('/usr/bin/say', ['-v', VOICE, to_say])
        reply = {'method': 'reply', 'payload': 'ok'}
        self.sendMessage("Controller", reply)




