import cv2
import numpy as np
import math

imgPath = str(input("Image Path: "))
img = cv2.imread(imgPath,0)
height = float(input("Max Y(mm): "))
height = int(math.floor(height))
width = float(input("Max X(mm): "))
width = int(math.floor(width))
precision = float(input("Machine Sensivity(mm): "))
digit = len(str(precision).split(".")[1])
edge = float(input("Please enter the diameter of the cutting tool(mm): "))
team = int(input("Cutting tool number: "))
s = int(input("S value: "))
f = int(input("F value: "))
zMax = float(input("Max Z(mm): "))
zMin = float(input("Min Z(mm): "))
fileName = str(input("File Name"))+".txt"

img = cv2.imread(imgPath,0)
med_val = np.median(img)

low = int(max(0,(1 - 0.33)*med_val))
high = int(min(255,(1 + 0.33)*med_val))

edges = cv2.Canny(img,low,high)
listOfCoords = []

for idxY,y in enumerate(img):
    for idxX,x in enumerate(y):
        if x == 255:
            listOfCoords.append({"order":0,"x":idxX,"y":len(img)-idxY})

for coords in listOfCoords:
    if coords["y"] < 0:
        print(coords["y"])

print(listOfCoords)

orderV = 1
curX = 0
curY = 0
listOfCoords[0]["order"] = 1
x = 1

print("Pixel count: "+str(len(listOfCoords)))

maxX = 0
maxY = 0
minX = 0
minY = 0

for coords in listOfCoords:
    if coords["x"] < minX:
        minX = coords["x"]

    if coords["y"] < minY:
        minY = coords["y"]

for coords in listOfCoords:
    coords["x"] += minX

    coords["y"] += minY

for coords in listOfCoords:
    if coords["x"] > maxX:
        maxX = coords["x"]

    if coords["y"] > maxY:
        maxY = coords["y"]

xDivide = float(float(maxX)/float(width))
yDivide = float(float(maxY)/float(height))

lim = edge
if precision > lim:
    lim = precision
lim = int(float(float(len(listOfCoords)/(width*height))*lim))
if lim < 2:
    lim = 2

while True:
    while True:
        cur = list(filter(lambda coord: coord['order'] == orderV, listOfCoords))[0]
        curX = cur["x"]
        curY = cur["y"]
        
        giveOrder = True
        for coords in listOfCoords:
            if coords["order"] == 0 and giveOrder:
                if (((abs(coords["y"] - curY) < lim)) and ((abs(coords["x"] - curX) < lim))) or (coords["y"] == curY and ((abs(coords["x"] - curX) < lim))) or (coords["x"] == curX and ((abs(coords["y"] - curY) < lim))):
                    orderV += 1
                    coords["order"] = orderV
                    giveOrder = False
        
        if giveOrder:
            break
                

    orderZeroList = list(filter(lambda coord: coord['order'] == 0, listOfCoords))
    print("Calculated "+str(len(listOfCoords)-len(orderZeroList))+" of "+str(len(listOfCoords))+" pixels")

    if len(orderZeroList) > 0:
        orderZeroChosen = orderZeroList[0]
        dist = int(((abs(orderZeroList[0]["x"] - curX)**2) + (abs(orderZeroList[0]["y"] - curY)**2))**0.5)
        for coords in orderZeroList:
            if int(((abs(coords["x"]-curX)**2) + (abs(coords["y"]-curY)**2))**0.5) < dist:
                orderZeroChosen = coords
                dist = int(((abs(coords["x"]-curX)**2) + (abs(coords["y"]-curY)**2))**0.5)
        
        orderV += 2
        for idx,coords in enumerate(listOfCoords):
            if coords == orderZeroChosen:
                listOfCoords[idx]["order"] = orderV

    else:
        print("Done")
        break

for coords in listOfCoords:
    coords["x"] = round(float(round(float(float(float(coords["x"])/xDivide)/precision))*precision),digit)
    coords["y"] = round(float(round(float(float(float(coords["y"])/yDivide)/precision))*precision),digit)

print(listOfCoords)
orderMax = 1
for coords in listOfCoords:
    if coords["order"] > orderMax:
        orderMax = coords["order"]

lineCount = 9 + ((orderMax-len(listOfCoords)) * 2) + len(listOfCoords)

with open(fileName,"w",encoding="utf-8") as file:
    file.write("G90 G21 G17 G80 G40 G54\nT"+str(team)+" M06\nS"+str(s)+". M03\nG00 X0. Y0. Z"+str(zMax/10)+"\n")
    onLine = 4
    print("Written "+str(onLine)+" of "+str(lineCount)+" lines")
    orderV = 1
    started = False
    while True:
        try:

            if started:
                file.write("G01 X"+str(list(filter(lambda coord: coord['order'] == orderV, listOfCoords))[0]["x"])+" Y"+str(list(filter(lambda coord: coord['order'] == orderV, listOfCoords))[0]["y"])+"\n")
                orderV += 1
                onLine += 1
                print("Written "+str(onLine)+" of "+str(lineCount)+" lines")

            else:
                file.write("G00 X"+str(list(filter(lambda coord: coord['order'] == orderV, listOfCoords))[0]["x"])+" Y"+str(list(filter(lambda coord: coord['order'] == orderV, listOfCoords))[0]["y"])+"\n")
                file.write("G01 Z"+str(zMin)+" F"+str(f)+"\n")
                orderV += 1
                started = True
                onLine += 2
                print("Written "+str(onLine)+" of "+str(lineCount)+" lines")

        except IndexError:
            try:
                orderV += 1
                if (((float((list(filter(lambda coord: coord['order'] == orderV-2, listOfCoords))[0]["x"]) - float(list(filter(lambda coord: coord['order'] == orderV, listOfCoords))[0]["x"]))**2) + (float((list(filter(lambda coord: coord['order'] == orderV-2, listOfCoords))[0]["y"]) - float(list(filter(lambda coord: coord['order'] == orderV, listOfCoords))[0]["y"]))**2))**0.5) > edge:
                    file.write("G01 Z"+str(zMax/10)+"\n")
                    file.write("G00 X"+str(list(filter(lambda coord: coord['order'] == orderV, listOfCoords))[0]["x"])+" Y"+str(list(filter(lambda coord: coord['order'] == orderV, listOfCoords))[0]["y"])+"\n")
                    file.write("G01 Z"+str(zMin)+"\n")

                else:
                    file.write("G01 X"+str(list(filter(lambda coord: coord['order'] == orderV, listOfCoords))[0]["x"])+" Y"+str(list(filter(lambda coord: coord['order'] == orderV, listOfCoords))[0]["y"])+"\n")
                orderV += 1
                onLine += 3
                print("Written "+str(onLine)+" of "+str(lineCount)+" lines")
            except IndexError:
                break
    
    file.write("G01 Z"+str(zMax/10)+"\nG00 X0. Y0. Z"+str(zMax)+"\nM30")

print("Decreasing line count")
while True:
    for i in range(3):
        idxPop = []
        with open(fileName,"r",encoding="utf-8") as file:
            lines = file.readlines()
            for idx,line in enumerate(lines):
                if (line.startswith("G01") and "Z" not in line) and (lines[idx+1].startswith("G01") and "Z" not in lines[idx+1]):
                    coords1 = line
                    coords2 = lines[idx+1]

                    if coords1 == coords2:
                        idxPop.append(idx+1)

        if idxPop != []:
            idxPop.sort()
            idxPop.reverse()
            for i in idxPop:
                lines.pop(i)
            with open(fileName,"w",encoding="utf-8") as file:
                for line in lines:
                    file.write(line)
            idxPop = []

    with open(fileName,"r",encoding="utf-8") as file:
        lines = file.readlines()
        for idx,line in enumerate(lines):
            if (line.startswith("G01") and "Z" not in line) and (lines[idx+1].startswith("G01") and "Z" not in lines[idx+1]):
                coords1 = line.split(" ")
                coords2 = lines[idx+1].split(" ")
                liste = lines

                if coords1[1] == coords2[1]:
                    idxPop.append(idx+1)

    if idxPop != []:
        idxPop.sort()
        idxPop.reverse()
        for i in idxPop:
            lines.pop(i)
        with open(fileName,"w",encoding="utf-8") as file:
            for line in lines:
                file.write(line)
        idxPop = []

    with open(fileName,"r",encoding="utf-8") as file:
        lines = file.readlines()
        for idx,line in enumerate(lines):
            if (line.startswith("G01") and "Z" not in line) and (lines[idx+1].startswith("G01") and "Z" not in lines[idx+1]):
                coords1 = line.split(" ")
                coords2 = lines[idx+1].split(" ")

                if coords1[2] == coords2[2]:
                    idxPop.append(idx+1)

    if idxPop != []:
        idxPop.sort()
        idxPop.reverse()
        for i in idxPop:
            lines.pop(i)
        with open(fileName,"w",encoding="utf-8") as file:
            for line in lines:
                file.write(line)
    else:
        break
print("Finished with "+str(len(lines))+" lines")