//
//  Declarations.swift
//  Distributed Systems-lab5
//
//  Created by 0xCA7 on 23/06/2021.
//

import Foundation

class System{
    var nodes:[Node]
    var centralNode:CentralNode
    var processes:[Process]
    public static var numberOfProcesses:Int = 0
    
    init(nodeNames:[String], nrOfProcesses:Int) {
        self.nodes = [Node]()
        self.processes = [Process]()
        System.numberOfProcesses = nrOfProcesses
        
        // Initialize lists of nodes, processes and resources
        for name in nodeNames {
            self.nodes.append(Node(name: name))
        }
        
        for i in 0..<nrOfProcesses {
            self.processes.append(Process(pid:i))
        }
        
        // Initialize central node
        self.centralNode = CentralNode(nrOfProcesses: nrOfProcesses)
    }
    
    // Main loop in the program
    func startAnimation(){
        while true{
            self.nodes.forEach {
                // Choose random process for a node
                //$0.startProcess(process: self.processes[Int.random(in: 0..<self.processes.count)])
                // Choose random resource for a process
                //$0.runProcess(processTable: self.processes)
                // Print current system state
                $0.printState()
            }
            
            self.nodes[0].processTable.append(self.processes[1])
            self.nodes[0].processTable[0].getLockedBy(process: self.processes[3])
            
            self.nodes[1].processTable.append(self.processes[3])
            self.nodes[1].processTable[0].getLockedBy(process: self.processes[0])
            
            self.nodes[2].processTable.append(self.processes[0])
            self.nodes[2].processTable[0].getLockedBy(process: self.processes[1])
            
            self.printSystemState()
            self.probeNodes()
            
            // clear screen
            sleep(3)
            print(terminator: Array(repeating: "\n", count: 100).joined())
        }
    }
    
    // Ask all nodes in the network for their R and P tables
    func probeNodes(){
        
        for node in self.nodes{
            // Set record in WFG Matrix if process points to another process
            for process in node.processTable{
                if (process.lockedBy != nil){
                    centralNode.WFGMatrix[process.pid][process.lockedBy!.pid] = 1
                    // Step 1. Block phase - adjusting public values of blocked process
                    process.inc()
                }
            }
        }
        
        
        
        // Check if there are no deadlocks
        if self.detectDeadlock(){
            print("Deadlock detected!")
            exit(-1)
        }
    }
    
    func detectDeadlock() -> Bool {
        // For each element if WFG Matrix
        for (r, row) in self.centralNode.WFGMatrix.enumerated(){
            for (c, item) in row.enumerated(){
                // Step 2 - transmission phase
                // If item equals 1
                if item != 0{
                    
                    // Go to resource or process that current resource/process points to
                    // If current item is 1, then we are process, pointing to resource
                    // If current item is -1, then we are resource, pointing to process
                    if self.processes[c].pv > self.processes[r].pv{
                        self.processes[r].pv = self.processes[c].pv
                        self.processes[r].uv = self.processes[c].pv
                    }else if self.processes[c].pv == self.processes[r].pv{
                        return true
                    }
                }
            }
        }
        
        return false
    }
    
    func printSystemState(){
        print("""
            ----------\
            \nSystem:\
            \nPT: \(self.getProcessTable())
            """)
    }
    
    func getProcessTable() -> String{
        var table:String = "[ "
        
        self.processes.forEach {
            if $0.lockedBy != nil{
                table.append("(\($0.pid))-> \($0.lockedBy?.pid ?? -1) ")
            }
        }
        table.append("]")
        
        return table
    }
}

class CentralNode{
    var WFGMatrix:[[Int]]
    
    init(nrOfProcesses:Int) {
        self.WFGMatrix = [[Int]]()
        
        // Initialize WFG Matrix with empty values
        // WFG Matrix has the following shape:
        //    P1 P2 P3 ...
        // P1
        // P2
        // P3
        // ...
        for _ in 0..<nrOfProcesses {
            var temparr = [Int]()
            for _ in 0..<nrOfProcesses {
                temparr.append(0)
            }
            
            self.WFGMatrix.append(temparr)
        }
    }
}

class Node{
    var processTable:[Process] = [Process]()
    var name:String
    
    init(name:String) {
        self.name = name
    }
    
    // Find random process and start executing it
    func startProcess(process:Process){
        self.processTable.append(process)
    }
    
    // For each process in process table, get resource it needs
    // and start "executing"
    func runProcess(processTable:[Process]){
        self.processTable.forEach{
            var i = Int.random(in: 0..<processTable.count)
            while i == $0.pid{
                i = Int.random(in: 0..<processTable.count)
            }
            $0.getLockedBy(process: processTable[i])
        }
    }
    
    func printState(){
        print("Node [\(self.name)] - PT: \(self.getProcessTable())")
    }
    
    func getProcessTable() -> String{
        var table:String = "[ "
        
        self.processTable.forEach {
            table.append("(\($0.pid))-> \($0.lockedBy?.pid ?? -1) ")
        }
        table.append("]")
        
        return table
    }
}

class Process{
    var pid:Int
    var lockedBy:Process?
    // Public value
    var pv:Int
    // Private value
    var uv:Int
    
    init(pid:Int) {
        self.pid = pid
        self.pv = Int.random(in: 0...System.numberOfProcesses)
        self.uv = self.pv
    }
    
    // Become locked by given process
    func getLockedBy(process:Process){self.lockedBy = process}
    
    // increase public value and priv value
    // so that they are greater than current values,
    // and current values of lockedBy node (that current node/process is waiting for)
    func inc(){
        let newValues = max(self.pv, self.uv, self.lockedBy!.pv, self.lockedBy!.uv) + 1
        //Int.random(in: max(self.pv, self.uv, self.lockedBy!.pv, self.lockedBy!.uv)...System.numberOfProcesses * 10)
        self.pv = newValues
        self.uv = newValues
    }
}
