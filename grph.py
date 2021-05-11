from sys import argv 
from re import findall, match, search, finditer
from collections import Counter

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
    for node in self.graph.keys():
      self.graphlvls[node] = 0
      for item in self.graph[node]:
        self.graphlvls[node] += self.nestLevel(self.graph[item] 
                               if item in self.graph else None)
    print(f"[*] Best node: ", *Counter(self.graphlvls).most_common()[0], "(paths)")
    #
  # Reach next node, and call this function
  # for all next nodes
  def nestLevel(self, item):
    if not item:
      return 1

    max_level = 1
    for sub in item:
        max_level += self.nestLevel(self.graph[sub] 
                    if sub in self.graph else None)

    return max_level
  #
#


if __name__ == '__main__':
  if not argv[1:]:
    print("[!] Graphs must be passed as argument. Example: \n$> grph.py A{B} B{C,D,E} C{E} E{D} ")
    exit(-1)
  trv = Traverser(argv)
  trv.countNestedLevels()
  
