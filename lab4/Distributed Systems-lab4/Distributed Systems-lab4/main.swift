//
//  main.swift
//  Distributed Systems-lab4
//
//  Created by 0xCA7 on 19/06/2021.
//

import Foundation

var sys = System(nodeNames: ["A", "B", "C", "D"], nrOfProcesses: 6, nrOfResources: 8)
sys.startAnimation()


