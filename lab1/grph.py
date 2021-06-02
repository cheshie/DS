from sys import argv 
from re import findall, match, search, finditer
from collections import Counter
from itertools import chain
flatten = lambda x : list(set(list(chain.from_iterable(x))))

"""
This program accepts the graph paths as parameter. Form of input is as follows: 
For this directed graph:

A ----> B ----> C  (B points to D, E and C points to E)
        | \    /
        \/ \/ \/
        D <- E

grph.py A{B} B{C,D,E} C{E} E{D} 
Other example:
"E{A,B}", "A{E,D,C}", "D{B}", "C{B,D}", "B{D}"
"""

class Traverser():
  def __init__(self, argv):
    self.graph = {}
    self.graphlvls = {}
    self.ParseInput(argv)
  #
  def ParseInput(self, argv):
    # Extract nodes from input
    nodes = [search(r"([A-Z])\{", el).group(1) for el in argv]

    # Identified nodes presentation
    if not nodes:
      print("[!] No valid nodes identified. Check your input. ")
    print(f"[*] {len(nodes)} nodes identified: {nodes}")

    # Create list of connected nodes for each node
    for node in nodes: 
      tmp = search(node+"\{(([A-Z]),?)+\}", ' '.join(argv)).group(0).strip(node)
      self.graph[node] = tmp.strip('{}').split(',')
  #
  def countNestedLevels(self):
    self.lastItems = []
    self.graphlvls = \
    dict((node, flatten(self.nestLevel([node]))) for node in self.graph.keys())
  #

  # Reach next node, and call this function
  # for all next nodes
  def nestLevel(self, item):
    if not item:
      return []

    # Add current item to a list of recently visited nodes
    self.lastItems += [item]
    # If this list contains duplicates, cycles detected
    # If so, break to recursion and clear recently visited nodes
    lastItems_flat = list(chain.from_iterable(self.lastItems))
    if len(lastItems_flat) != \
          len(set(lastItems_flat)):
      self.lastItems = []
      return []

    max_level = [item]
    for sub in item:
      it = self.nestLevel(self.graph[sub] 
                    if sub in self.graph else None)
      max_level += it

    return max_level
  #

  def getBestNode(self):
    best_nodes = Counter(dict((x, len(self.graphlvls[x])) 
                  for x in self.graphlvls)).most_common()
    print("[*] Best node: ", best_nodes[0][0], ' -> ', self.graphlvls[best_nodes[0][0]])
    print("[*] Other nodes: ")
    for node in best_nodes[1:]:
      print("[*] Node: ", node[0], " -> ", self.graphlvls[node[0]])
#


if __name__ == '__main__':
  if not argv[1:]:
    print("[!] Graphs must be passed as argument. Example: \n$> grph.py A{B} B{C,D,E} C{E} E{D} ")
    exit(-1)
  trv = Traverser(argv[1].split())
  trv.countNestedLevels()
  trv.getBestNode()
  
