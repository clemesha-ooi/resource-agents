#!/usr/bin/env python
import time
import random

from fsm import FSM


def do_start(fsm):
    print "=*=*= do_start =*=*= current_state=%s" % fsm.current_state

def do_reload(fsm):
    print "==do_reload == current_state=%s" % fsm.current_state

def do_default(fsm):
    if fsm.input_symbol == "FATAL_BLAH":
        raise "FATAL_BLAH"
    print "=do_default= current_state=%s" % fsm.current_state
    #elif fsm.input_symbol == "RUNNING"
     #   raise "FATAL_BLAH"

def running_ok(fsm):
    print "~~~ running_ok ~~~ current_state=%s" % fsm.current_state

def error(fsm):
    print "==error== input_symbol=%s" % fsm.input_symbol


"""
'START' is the given Action (input_symbol)
The current_state = 'INIT' of the FSM

(input_symbol, current_state) --> (action, next_state)

"""
def create_new_fsm():
    f = FSM("INIT", [])
    f.set_default_transition(do_default, "INIT")
    f.add_transition("START", "INIT", do_start, "RUNNING")
    f.add_transition("STOP", "RUNNING", do_start, "INIT")
    f.add_transition_list(["START", "INIT", "RELOAD", "RESTART"], "RUNNING", running_ok, "RUNNING")
    return f



STATES = ["UN_INIT" "RUNNING", "STOPPED" "ERROR"]
ACTIONS = ["INIT", "START", "STOP", "RELOAD", "RESTART", "RUN_SCRIPT", "BLAH_BLAH", "FATAL_BLAH"]
"""
while 1:
    time.sleep(2)
    action = random.choice(ACTIONS)
    print "\nACTION=>",action, " - process=>",f.process(action)
"""
