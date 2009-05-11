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



