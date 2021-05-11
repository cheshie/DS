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
    self.graphlvls = \
    dict((node, flatten(self.nestLevel([node]))) for node in self.graph.keys())
  #

  # Reach next node, and call this function
  # for all next nodes
  def nestLevel(self, item):
    if not item:
      return []

    max_level = [item]
    for sub in item:
        max_level += self.nestLevel(self.graph[sub] 
                    if sub in self.graph else None)

    return max_level
  #

  def getBestNode(self):
    best_nodes = Counter([(x, len(self.graphlvls[x]))for x in self.graphlvls]).most_common()
    print("[*] Best node: ", best_nodes[0][0][0], ' -> ', self.graphlvls[best_nodes[0][0][0]])
    print("[*] Other nodes: ")
    for node in best_nodes:
      print("[*] Node: ", node[0][0], " -> ", self.graphlvls[node[0][0]])
#


if __name__ == '__main__':
  argv = ["A{B}", "B{C,D,E}", "C{E}", "E{D}"]
  #argv = ["E{A,B}", "A{E,D,C}", "D{B}", "C{B,D}", "B{D}"]
  if not argv[1:]:
    print("[!] Graphs must be passed as argument. Example: \n$> grph.py A{B} B{C,D,E} C{E} E{D} ")
    exit(-1)
  trv = Traverser(argv)
  trv.countNestedLevels()
  trv.getBestNode()
  