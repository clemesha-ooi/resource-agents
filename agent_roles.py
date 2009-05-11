import os
import pwd
import sys
from twisted.internet.utils import getProcessOutput
from twisted.internet import defer
from twisted.python import log

sys.path.append("../magnet")
from magnet import pole
from magnet import field

from osx_resource import disk_space

class Say(pole.ResourceCapability):
    """
    """
    def sendOK(self, result):
        reply = {'method': 'reply', 'payload': 'ok'}
        self.sendMessage(reply, 'test')

    def sendError(self, failure):
        reply = {'method': 'reply', 'payload': 'got an error running say'}
        self.sendMessage(reply, 'test')

    def action_say(self, message_object):
        to_say = message_object['payload']
        log.msg('Got say message: %s' % message_object['payload'])
        d = getProcessOutput('/usr/bin/say', ['-v', 'Fred', to_say])
        d.addCallback(self.sendOK).addErrback(self.sendError)
        return None


class Disk(pole.ResourceMonitorRole):
    def sendOK(self, result):
        reply = {'method': 'reply', 'payload': 'ok'}
        self.sendMessage(reply, 'test')

    def sendError(self, failure):
        reply = {'method': 'reply', 'payload': 'got an error running Disk'}
        self.sendMessage(reply, 'test')

    @defer.inlineCallbacks
    def action_disk(self, message_object):
        used, avail = yield disk_space()
        name = pwd.getpwuid(os.getuid())[4].split(" ")[0] 
        say = "Hello %s.  Your resource has %d gigabytes free disk, and %d used." % (name, avail, used)
        print "=========", say
        result = yield getProcessOutput('/usr/bin/say', ['-v', 'Fred', say])
        self.sendOK("ok")
        #d.addCallback(self.sendOK).addErrback(self.sendError)







