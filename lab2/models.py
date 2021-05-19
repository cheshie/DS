from datetime import datetime, timedelta
from dataclasses import dataclass
from random import choice, randint
from enum import Enum
from threading import Thread
from time import sleep
from lab2 import *
from sys import stdout
from os import system
from sys import argv

class State(Enum):
  CRITICALSTATE = 0x00
  CANDIDSTATE   = 0x01
  IDLESTATE     = 0x02

class Decision(Enum):
  REQUEST = 0x00
  APPROVE = 0x01
  
class Request:
  def __init__(self, sender:Node, requestType:Decision=Decision.REQUEST, timestamp:datetime=datetime.now()):
    self.timestamp   = timestamp
    self.sender      = sender
    self.requestType = requestType
  #
  def __repr__(self):
    return f"RQ({self.sender.name})"
  #
  def __hash__(self):
    return hash(self.__repr__())
  #
  def __eq__(self, other):
    if isinstance(other, Request):
      return self.sender.name == other.sender.name
    return False
  #
#