from models import *
# 1. There are X nodes
# 2. One node is in CS, each node can be either candidate or not (random)
# 3. Candidate sends requests to all nodes, if all nodes reply, it takes CS 
# 4. After CS node finishes its computation, it finds node that sent their 
#    request earlier to pass CS to it 

class Node(object):  
  def __init__(self, name):
    # Name of the node
    self.name = name
    # If current state is CRITICALSTATE, deadline determines 
    # when the node will get back to IDLESTATE
    self.deadline = None
    # Request Queue, keeps track of requests sent to this node
    # that are requesting its approval
    self.reqQ = set()
    # Approval Queue, keeps track of nodes that approved this node
    # as the new CRITICALSTATE
    self.appQ = set()
    # Set state randomly to either CANDIDATE OR IDLE
    self.setState()
  #

  # Set state of created node to either idle 
  # or applying for CS
  def setState(self):
    if randint(0,100) < 50:
      self.state = State.CANDIDSTATE
    else:
      self.state = State.IDLESTATE
  #

  # This function gets called as a thread so that each of 
  # nodes runs separately in a loop
  def doWork(self, nodeslist : list['Node']):
    while True:
      # If current node is in critical state
      if self.state is State.CRITICALSTATE:
        # If deadline reached - go to idle state
        if datetime.now() > self.deadline:
          self.state = State.IDLESTATE
          # Get best candidate for next Critical State (CS)
          if len(list(self.reqQ)):
            # Get first candidate as first arbitrarily chosen
            candidate = list(self.reqQ)[0]
            # iterate over other candidates, if there is candidate
            # with older timestamp, it's new best candidate to CS
            for reqS in self.reqQ:
              if candidate.timestamp > reqS.timestamp:
                candidate = reqS
            # If candidate chosen, send node's approval to it
            self.sendApproval(recipent=candidate.sender)

      # If current node is a CANDIDATE for CS
      if self.state is State.CANDIDSTATE:
        # Send request to all other nodes
        self.requestCS(nodeslist)
        # Check up with current CS node whether it has 
        # request from another node that is from earlier
        # (and therefore is better candidate for CS)
        self.queryCurrentCSNode(nodeslist)
      
      # If current node is IDLE
      if self.state is State.IDLESTATE:
        # Send approval to all nodes that requested it
        # and remove their request from queue
        copyReqQ = self.reqQ.copy()
        for req in copyReqQ:
          self.sendApproval(recipent=req.sender)
          self.reqQ.remove(req)
        # Get new random state - either IDLE or CANDIDATE
        self.setState()
      sleep(2)
  #

  # Query current CS node whether there are
  # better candidates for new CS than current node
  def queryCurrentCSNode(self, nodeslist):
    # Find critical node from current list of all nodes
    criticalNode = None
    for node in nodeslist:
      if node.state == State.CRITICALSTATE:
        criticalNode = node
    
    # If critical node found
    if criticalNode != None:
      # With the list of requests that CS node received
      # find node that has the oldest timestamp, and 
      # therefore is the best candidate
      if len(list(criticalNode.reqQ)):
        oldestReq = list(criticalNode.reqQ)[0]
        for req in criticalNode.reqQ:
          if oldestReq.timestamp > req.timestamp:
            oldestReq = req
        
        # If found candidate is not the current node, 
        # send approval to it (so that two CANDIDATEs will
        # not block each other)
        if oldestReq.sender.name != self.name:
          self.sendApproval(recipent=oldestReq.sender)
          criticalNode.reqQ.remove(oldestReq)
  #

  # Sends request to all nodes in the nodeslist
  # Asking for their reply so that it could overtake CS
  # Request must contain timestamp
  def requestCS(self, nodeslist : list['Node']):
    for node in nodeslist:
      if node != self:
        rq = Request(sender=self)
        node.receiveReq(rq)
  #

  # For newly created CS node, set deadline for their CS state
  def setDeadline(self, deadline):
    self.deadline = deadline
  #

  # Send Approve request to the node requesting it
  def sendApproval(self, recipent : 'Node'):
    recipent.receiveReq(Request(sender=self, requestType=Decision.APPROVE))
  #

  # Add received request to the queue. If currently not applying for CS, 
  # reply to request. If in CS or applying, do not reply to request
  # but only add it to request queue 
  def receiveReq(self, req):
    # If any node, in any state receives request, add it
    # to the queue of requests
    if req.requestType == Decision.REQUEST:
        self.reqQ.add(req)

    # If its IDLE node, send approval to the best 
    # candidate on their list of requests
    if self.state == State.IDLESTATE:
      # Get best candidate for next CS
      if len(list(self.reqQ)):
        candidate = list(self.reqQ)[0]
        for reqS in self.reqQ:
          # find best candidate with oldest timestamp
          if candidate.timestamp > reqS.timestamp:
            candidate = reqS
        self.sendApproval(recipent=candidate.sender)

    # If current node is a CANDIDATE, and received
    # request is of type APPROVE, add this approval
    # to the queue
    elif self.state == State.CANDIDSTATE:
      if req.requestType == Decision.APPROVE:
        self.appQ.add(req)
  #
  def __repr__(self):
    return f"Node({self.name})"
  #
  def __hash__(self):
    return hash(self.__repr__())
  #
#

class Network:
  def __init__(self, listOfNodes : list([Node])):
    # deadline for CS to get out of CS state
    self.seconds = 5
    # list of nodes in the simulation
    self.nodes   = listOfNodes
    # nodes running as separate threads
    self.running = []
    # choose first CS node
    self.setCSnode()
    # Start simulation
    self.simulateNetwork()
  #

  # Set random node to CS
  def setCSnode(self):
    # Chose random node, assign CS state to it and add deadline
    self.chosenNode = choice(self.nodes)
    self.chosenNode.state = State.CRITICALSTATE
    self.chosenNode.setDeadline(datetime.now() + timedelta(seconds=self.seconds))
  #

  def simulateNetwork(self):
    system('clear')
    for node in self.nodes:
      # Start all nodes in separate threads
      p = Thread(target=node.doWork, args=(self.nodes,))
      self.running.append(p)
      p.start()
    try:
      while True:
        # Print status of all nodes
        print(f"[*] Critical node chosen: Node({self.chosenNode.name})")
        for node in self.nodes:
            rQ  = f'rQ: [list({node.reqQ})]'
            apQ = f'apQ: [list({node.appQ})]'
            print(f"[*] Node({node.name}-{str(node.state).replace('State.','')}) -  {rQ:>5} {apQ:>5}")
        # Find node that has all required approvals 
        # so that it could become new CS node
        for node in self.nodes:
          if len(list(node.appQ)) == len(self.nodes) - 1:
            node.state = State.CRITICALSTATE
            node.setDeadline(datetime.now() + timedelta(seconds=self.seconds))
            node.appQ = set()
            self.chosenNode = node
        sleep(2)
        system('clear')
    except KeyboardInterrupt:
      return
  #

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_value, traceback):
    for node in self.running:
       node.join()
    

if __name__ == "__main__":
  net = Network([Node('A'), Node('B'), Node('C')])