from collections import namedtuple
from random import choice, randint
from time import sleep
from threading import Thread
from datetime import datetime, timedelta
from os import system

class Site:
  def __init__(self, name, holder=None):
    # Queue stores info about neighbors that have sent 
    # a request for the token to he site Si
    # Non-empty indicates that the site has 
    # sent a REQ to the root
    self.request_q : list[Site] = []
    # Pointing to a neighbor 
    self.holder:Site = holder
    # Name of the node
    self.name = name
    # If already worked in Critical Section
    self.workedInCS = False
  #
  def request(self, requestingNode):
    sleep(1)
    System.printState()
    # If request_q is empty, send request to parent
    # and if previously not worked in cs
    if not len(self.request_q):
      self.push(requestingNode)
      # If not the root node
      if self.holder:
        # If haven't already worked in CS, request it
        self.holder.request(self)
      # If its root node, and work is finished, pass token
      else:
        # Wait until token is released
        while System.csTaken:
          sleep(0.25)
          System.csTaken = System.checkCS()
        # Get node that was requesting token and pass token to it
        descendant = self.pop()
        self.holder = descendant
        self.holder.passToken()
  #
  def pop(self):
    return self.request_q.pop()
  #
  def push(self, value):
    self.request_q.append(value)
  #
  def setHolder(self, holder):
    self.holder = holder
  #
  def passToken(self):
    sleep(1)
    if len(self.request_q):
      descendant = self.pop()
      # If current node has only itself on the queue
      if descendant == self:
        # Then it means it requested the CS
        # So start work, mark itself as currently holding CS
        System.currentCS = self
        self.workedInCS = True
        self.holder = None
        System.doCSWork()
        System.done.append(self)
      # If current node has another descendant in the queue
      # Pass token to first descendant
      else:
        # reverse the tree
        self.holder = descendant
        # Pass token to next Node
        descendant.passToken()
#

# A (B(D,E),C(F,G))
class System:
  csTaken    = False
  deadlineCS = None
  currentCS  = None
  newCSCandidate= None
  done = []
  nodes = None

  def __init__(self):
    names = ['A','B','C','D','E','F','G']
    nodeslist = namedtuple('nodes', names)
    System.nodes = nodeslist(*[Site(name) for name in names])
    # Current root is also CS node
    System.currentCS = self.nodes.A
    System.currentCS.workedInCS = True
    # nodes that already finished their CS
    System.done.append(System.currentCS) 
    self.setStructure()
  #

  def getRandomNode(self):
    return choice(list(set(self.nodes) - set(System.done)))
  #

  def setStructure(self):
    System.nodes.E.setHolder(System.nodes.B)
    System.nodes.D.setHolder(System.nodes.B)
    System.nodes.F.setHolder(System.nodes.C)
    System.nodes.G.setHolder(System.nodes.C)
    System.nodes.B.setHolder(System.nodes.A)
    System.nodes.C.setHolder(System.nodes.A)
  #

  @classmethod
  def doCSWork(cls, timeToWork=randint(3,8)):
    System.csTaken = True
    # time for the current CS node to 
    # finish its work and pass token
    System.deadlineCS = datetime.now() +\
       timedelta(seconds=timeToWork)
    #

  # Check whether node finished its CS
  @classmethod
  def checkCS(cls):
    return datetime.now() > System.deadlineCS
  #

  def animate(self):
    # First node that enters its CS
    System.doCSWork()

    try:
      while True:
        # Get next candidate for CS
        System.newCSCandidate = self.getRandomNode()
        # Candidate must push itself into its queue
        System.newCSCandidate.push(System.newCSCandidate)
        # Request CS token from parent
        System.newCSCandidate.holder.request(System.newCSCandidate)

        # Conditions for ending animation: if all nodes had token once
        if len(self.done) == 7:
          print("Finished. Order in which nodes requested CS: ")
          print(*[x.name for x in self.done])
          print("Exiting.")
          exit(0)
        System.newCSCandidate = self.getRandomNode()

    except KeyboardInterrupt:
      exit(0)
    #
  
  # prints current state of the network
  @classmethod
  def printState(cls):
        system('clear')
        print(f"[{System.currentCS.name}] Currently in CS. Deadline: [{System.deadlineCS.strftime('%H:%M:%S')}]")
        for node in System.nodes:
          state = 'Waiting'
          if System.newCSCandidate == node:
            state = 'Applying'
          if node.workedInCS:
            state = 'Done'
          print(f"[{node.name}] Node [{state}] ::=> "
          f"[{node.holder.name if node.holder else None}] "
          f":: Que => {[x.name for x in node.request_q]}")
#

from sys import argv
print(argv)
exit()
net = System()
net.animate()