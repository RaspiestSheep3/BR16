from dataclasses import dataclass
from typing import Any 
import re

@dataclass
class Register:
    registerCode : int
    used : bool
    varName : str=None
    valueType : str=None
    valueHeld : Any=None
    isTemp : bool=False

filePath = "Input.py"

activeRegisters = {}
activeVariables = {}

#Prepping register list
for i in range(1,14):
    activeRegisters[i] = Register(registerCode=i, used=False)


lines = []
with open(filePath, "r") as fileHandle:
    lines = fileHandle.readlines()

outputLines = []

operations = ["+", "-", "*", "/"]

def FindOpenRegister():
    for register in activeRegisters.values():
        if(not register.used):
            return register

def ReduceExpression(partsRevisedFirstPass, operationSet = operations):
    counter = 1
    partsRevised = []
    while(counter < len(partsRevisedFirstPass)):
        if(partsRevisedFirstPass[counter] in operationSet):
            partsRevised.append(partsRevisedFirstPass[counter-1:counter+2])
            print(partsRevisedFirstPass[counter-1:counter+2])
            counter += 1
        else:
            partsRevised.append(partsRevisedFirstPass[counter-1])
            partsRevised.append(partsRevisedFirstPass[counter])
        counter += 2

    return partsRevised

def GenerateOperationAssembly(output, input,usedTempRegisters, isOutput=False, outputRegisterCode=None):
    commands = {"+" : "add", "-" : "sub", "*" : "mul"}
    
    if(isinstance(input[0], str)):
        if(input[0] in activeVariables):
            num1 = f"r{activeVariables[input[0]].registerCode}"
        else:
            num1 = input[0]
    elif(isinstance(input[0], list)):
        output, num1, _ = GenerateOperationAssembly(output, input[0], usedTempRegisters)
    else:
        print(type(num1))
    
    if(isinstance(input[2], str)):
        if(input[2] in activeVariables):
            num2 = f"r{activeVariables[input[2]].registerCode}"
        else:
            num2 = input[2]
    elif(isinstance(input[2], list)):
        output, num2, _ = GenerateOperationAssembly(output, input[2], usedTempRegisters)
    else:
        print(type(num2))

    if(isOutput):
        tempReg = activeRegisters[outputRegisterCode]
    else:
        tempReg = FindOpenRegister()
        activeRegisters[tempReg.registerCode].used = True
        activeRegisters[tempReg.registerCode].isTemp = True
        usedTempRegisters.add(tempReg.registerCode)
    
    output.append(f"{commands[input[1]]} r{tempReg.registerCode}, {num1}, {num2}\n")
    return output, f"r{tempReg.registerCode}", usedTempRegisters 

#print(lines)
for line in lines:
    #print(line)
    line = line.strip("\n")
    line = line.replace(" ", "")
    if(line == ""):
        continue
    
    #Ignoring comments
    if("#" in line):
        hashIndex = line.index("#")
        line = line[0:hashIndex]
    
    if("=" in line):
        #Setting a variable
        line = line.split("=")
        print(f"Line split : {line}")
        registerToUse = FindOpenRegister()
        registerToUse.used = True
        registerToUse.varName = line[0]
        activeVariables[line[0]] = registerToUse
        
        activeOperations = []
        for char in line[1]:
            if(char in operations):
                activeOperations.append(char)
        
        print(f"Operations : {activeOperations}")
        
        if(len(activeOperations) > 0):
            #Splitting into all the different steps
            escapeOps = [re.escape(op) for op in operations]
            pattern = r"\s*(" + "|".join(escapeOps) + r")\s*"
            
            parts = re.split(pattern, line[1])
            parts = [part.strip() for part in parts if part.strip()]
            
            print(f"parts {parts}")
            
            """
            partsRevisedFirstPass = []
            counter = 1
            while(counter < len(parts)):
                if(parts[counter] in {"*", "/"}):
                    partsRevisedFirstPass.append(parts[counter-1:counter+2])
                    print(parts[counter-1:counter+2])
                    counter += 1
                else:
                    partsRevisedFirstPass.append(parts[counter-1])
                    partsRevisedFirstPass.append(parts[counter])
                counter += 2"""
            
            partsRevisedFirstPass = ReduceExpression(parts, {"*", "/"})
            while("*" in partsRevisedFirstPass) or ("/" in partsRevisedFirstPass):
                partsRevisedFirstPass = ReduceExpression(partsRevisedFirstPass, {"*", "/"})
            
            print(f"Pass 1 : {partsRevisedFirstPass}")
            """counter = 1
            partsRevised = []
            while(counter < len(partsRevisedFirstPass)):
                if(partsRevisedFirstPass[counter] in operations):
                    partsRevised.append(partsRevisedFirstPass[counter-1:counter+2])
                    print(partsRevisedFirstPass[counter-1:counter+2])
                    counter += 1
                else:
                    partsRevised.append(partsRevisedFirstPass[counter-1])
                    partsRevised.append(partsRevisedFirstPass[counter])
                counter += 2"""
            
            partsRevised = ReduceExpression(partsRevisedFirstPass)
            while(len(partsRevised) > 3):
                partsRevised = ReduceExpression(partsRevised)
            
            print(f"partsRevised {partsRevised}")

            lineIndex = 0
            
            output, _, usedRegisters = GenerateOperationAssembly([], partsRevised, set(), True, 3)
            print(f"Assembly output for operations : {output}")
            print(f"Used registers : {usedRegisters}")
            outputLines += output
            
            #Cleaning up the old registers
            for usedReg in usedRegisters:
                activeRegisters[usedReg].used = False
            
            """for operationList in partsRevised:
                commands = {"+" : "add", "-" : "sub", "*" : "mul"}
                commandWord = commands[operationList[1]]
                
                lineSet = [operationList[0], operationList[2]]
                print(f"lineSet : {lineSet}")
                #print(f"Known variables : {activeVariables}")
                num1 = None
                num2 = None
                if(lineSet[0] == "result"):
                    num1 = f"r{registerToUse.registerCode}"
                elif(lineSet[0] in activeVariables):
                    num1 = f"r{activeVariables[lineSet[0]].registerCode}"
                else:
                    num1 = str(lineSet[0])
                
                if(lineSet[1] == "result"):
                    num2 = f"r{registerToUse.registerCode}"
                elif(lineSet[1] in activeVariables):
                    num2 = f"r{activeVariables[lineSet[1]].registerCode}"
                else:
                    num2 = str(lineSet[1])
                outputLines.append(f"{commandWord} r{registerToUse.registerCode}, {num1}, {num2}\n")
                lineIndex += 1"""
        else:
            if(line[1] in activeVariables):
                registerToUse.valueHeld = activeVariables[line[1]].valueHeld
                mov2 = f"r{activeVariables[line[1]].registerCode}"
            else:
                registerToUse.valueHeld = line[1]
                mov2 = line[1]
            registerToUse.valueType = str(type(line[1]))
            #print(registerToUse)
            #print(line)
            outputLines.append(f"mov r{registerToUse.registerCode}, {mov2}\n")

with open("OutputAssembly.asm", "w") as fileHandle:
    outputLines[-1] = outputLines[-1].strip("\n")
    fileHandle.writelines(outputLines)