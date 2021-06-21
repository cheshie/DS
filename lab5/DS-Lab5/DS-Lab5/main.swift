//
//  main.swift
//  Distributed Systems-lab5
//
//  Created by 0xCA7 on 23/06/2021.
//

import Foundation

// TODO: even for 40 processes, deadlock detected instantly
// something must be wrong with either detection or generating, as System PT is much longer
// than local PTs. Investigate

var sys = System(nodeNames: ["A", "B", "C", "D"], nrOfProcesses: 4)
sys.startAnimation()


