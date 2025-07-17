from dataclasses import dataclass
from typing import Any 

@dataclass
class Register:
    registerCode : int
    used : bool
    varName : str=None
    valueType : str=None
    valueHeld : Any=None

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

print(lines)
for line in lines:
    print(line)
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
        activeOperation = None
        for operation in operations:
            if(operation in line):
                activeOperation = operation
                break
        
        line = line.split("=")
        print(f"Line split : {line}")
        registerToUse = FindOpenRegister()
        registerToUse.used = True
        registerToUse.varName = line[0]
        activeVariables[line[0]] = registerToUse
        
        if(activeOperation):
            commands = {"+" : "add", "-" : "sub", "*" : "mul"}
            commandWord = commands[activeOperation]
            
            lineSet = line[1].split(activeOperation)
            print(f"lineSet : {lineSet}")
            print(f"Known variables : {activeVariables}")
            num1 = None
            num2 = None
            if(lineSet[0] in activeVariables):
                num1 = f"r{activeVariables[lineSet[0]].registerCode}"
            else:
                num1 = str(lineSet[0])
            if(lineSet[1] in activeVariables):
                num2 = f"r{activeVariables[lineSet[1]].registerCode}"
            else:
                num2 = str(lineSet[1])
            outputLines.append(f"{commandWord} r{registerToUse.registerCode}, {num1}, {num2}\n")
        else:
            if(line[1] in activeVariables):
                registerToUse.valueHeld = activeVariables[line[1]].valueHeld
                mov2 = f"r{activeVariables[line[1]].registerCode}"
            else:
                registerToUse.valueHeld = line[1]
                mov2 = line[1]
            registerToUse.valueType = str(type(line[1]))
            print(registerToUse)
            print(line)
            outputLines.append(f"mov r{registerToUse.registerCode}, {mov2}\n")

with open("OutputAssembly.txt", "w") as fileHandle:
    fileHandle.writelines(outputLines)
    
    
fileHandle = open("testfile.txt", "r")
lines = fileHandle.readlines() #Lines = ["line1\n", "line2\n"]
fileHandle.close()
lines[0] = "NewLine\n"
fileHandle = open("testfile.txt", "w")
fileHandle.writelines(lines)
fileHandle.write("line3")
fileHandle.close()