//
//  Declarations.swift
//  Distributed Systems-lab4
//
//  Created by 0xCA7 on 19/06/2021.
//

import Foundation

class System{
    var nodes:[Node]
    var centralNode:CentralNode
    var resources:[Resource]
    var processes:[Process]
    
    init(nodeNames:[String], nrOfProcesses:Int, nrOfResources:Int) {
        self.nodes = [Node]()
        self.processes = [Process]()
        self.resources = [Resource]()
        
        // Initialize lists of nodes, processes and resources
        for name in nodeNames {
            self.nodes.append(Node(name: name))
        }
        
        for i in 0..<nrOfProcesses {
            self.processes.append(Process(pid:i))
        }
        
        for i in 0..<nrOfResources {
            self.resources.append(Resource(rid: i))
        }
        
        // Initialize central node
        self.centralNode = CentralNode(nrOfProcesses: nrOfProcesses, nrOfResources: nrOfResources)
    }
    
    // Main loop in the program
    func startAnimation(){
        while true{
            self.nodes.forEach {
                // Choose random process for a node
                $0.startProcess(process: self.processes[Int.random(in: 0..<self.processes.count)])
                // Choose random resource for a process
                $0.runProcess(resourceTable: self.resources)
                // Choose random process for a resource
                $0.runResource(processTable: self.processes)
                // Print current system state
                $0.printState()
            }
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
            // Set record in WFG Matrix if process points to resource
            for process in node.processTable{
                if (process.heldResource != nil){
                    centralNode.WFGMatrix[process.pid][process.heldResource!.rid] = 1
                }
            }
            
            // Set record in WFG Matrix if resource points to a process
            for resource in node.resourceTable{
                if resource.heldProcess != nil{
                    centralNode.WFGMatrix[resource.heldProcess!.pid][resource.rid] = -1
                }
            }
            
            // Check if there are no deadlocks
            if self.detectDeadlock(){
                print("Deadlock detected!")
                exit(-1)
            }
        }
    }
    
    func detectDeadlock() -> Bool {
        // For each element if WFG Matrix
        for (r, row) in self.centralNode.WFGMatrix.enumerated(){
            for (c, item) in row.enumerated(){
                // If item equals 1
                if item != 0{
                    var visited = Set<String>()
                    visited.insert("P\(r)")
                    // Go to resource or process that current resource/process points to
                    // If current item is 1, then we are process, pointing to resource
                    // If current item is -1, then we are resource, pointing to process
                    if self.traverseGraph(next: c, visited: &visited, expect: item * -1){
                        return true
                    }
                }
            }
        }
        
        return false
    }
    
    func traverseGraph(next:Int, visited: inout Set<String>, expect:Int) -> Bool{
        
        // Deadlock (cycle) detected
        if visited.contains(expect == 1 ? "P\(next)" : "R\(next)"){
            return true
        }
        
        // Insert currently visited item to the set
        visited.insert(expect == 1 ? "P\(next)" : "R\(next)")
        
        // Enumerate matrix again
        for (r, row) in self.centralNode.WFGMatrix.enumerated(){
            for (c, item) in row.enumerated(){
                
                // Go to the next process
                if expect == -1 && c == next && item == expect{
                    if self.traverseGraph(next: r, visited: &visited, expect:1){return true}
                }
                
                // Go to the next resource
                if expect == 1 && r == next && item == expect{
                    if self.traverseGraph(next: c, visited: &visited, expect:-1){return true}
                }
            }
        }
        
        return false
    }
    
    func printSystemState(){
        print("""
            ----------\
            \nSystem:\
            \nPT: \(self.getProcessTable())\
            \nRT: \(self.getResourceTable())
            """)
    }
    
    func getProcessTable() -> String{
        var table:String = "[ "
        
        self.processes.forEach {
            table.append("(\($0.pid))-> \($0.heldResource?.rid ?? -1) ")
        }
        table.append("]")
        
        return table
    }
    
    func getResourceTable() -> String{
        var table:String = "[ "
        
        self.resources.forEach {
            table.append("(\($0.rid))-> \($0.heldProcess?.pid ?? -1) ")
        }
        table.append("]")
        
        return table
    }
}

class CentralNode{
    var WFGMatrix:[[Int]]
    
    init(nrOfProcesses:Int, nrOfResources:Int) {
        self.WFGMatrix = [[Int]]()
        
        // Initialize WFG Matrix with empty values
        // WFG Matrix has the following shape:
        //    R1 R2 R3 R4 ...
        // P1
        // P2
        // P3
        // ...
        for _ in 0..<nrOfProcesses {
            var temparr = [Int]()
            for _ in 0..<nrOfResources {
                temparr.append(0)
            }
            
            self.WFGMatrix.append(temparr)
        }
    }
}

class Node{
    var processTable:[Process] = [Process]()
    var resourceTable:[Resource] = [Resource]()
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
    func runProcess(resourceTable:[Resource]){
        self.processTable.forEach{
            $0.getResouce(resource: resourceTable[Int.random(in: 0..<resourceTable.count)])
            self.resourceTable.append($0.heldResource!)
        }
    }
    
    // For each resource in resource table, find process it
    // depends on
    func runResource(processTable:[Process]){
        self.resourceTable.forEach{
            $0.getProcess(process: processTable[Int.random(in: 0..<processTable.count)])
            self.processTable.append($0.heldProcess!)
        }
    }
    
    func printState(){
        print("""
            Node [\(self.name)] - PT: \(self.getProcessTable())   RT:\
            \(self.getResourceTable())
            """)
    }
    
    func getProcessTable() -> String{
        var table:String = "[ "
        
        self.processTable.forEach {
            table.append("(\($0.pid))-> \($0.heldResource?.rid ?? -1) ")
        }
        table.append("]")
        
        return table
    }
    
    func getResourceTable() -> String{
        var table:String = "[ "
        
        self.resourceTable.forEach {
            table.append("(\($0.rid))-> \($0.heldProcess?.pid ?? -1) ")
        }
        table.append("]")
        
        return table
    }
}

class Process{
    var pid:Int
    var heldResource:Resource?
    
    init(pid:Int) {
        self.pid = pid
    }
    
    // Lock given resource
    func getResouce(resource:Resource){
        self.heldResource = resource
    }
}

class Resource{
    var rid:Int
    var heldProcess:Process?
    
    init(rid:Int) {
        self.rid = rid
    }
    
    // Lock given process
    func getProcess(process:Process){
        self.heldProcess = process
    }
}
