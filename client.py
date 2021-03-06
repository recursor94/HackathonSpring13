#Team Midas
import socket
import math

#Globals
Revenue = 0
W_cost = 0
J_cost = 0
D_cost = 0

Demand = {}
Config = {}

foo = []

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#creates a connection to the game server and starts the game
def init():
    global s
    s.connect(("hackathon.hopto.org", 27832))
    s.send("INIT Midas")
    data = s.recv(1024)
    print data
    s.send("RECD")
    data = s.recv(1024)
    print data
    parseCost(data)
    s.send("START")
    data = s.recv(1024)
    return data

#parses cost data and stores it in the respective globals
def parseCost(data):
    global Revenue 
    global W_cost
    global J_cost
    global D_cost
    cost = data.split()
    Revenue = int(cost[1])
    W_cost = int(cost[2])
    J_cost = int(cost[3])
    D_cost = int(cost[4])
    print "REVENUE "+ str(Revenue)
    print "WEB " + str(W_cost)
    print "Java " + str(J_cost)
    print "Data " + str(D_cost)
    print ""

def move():
    global Revenue
    global W_cost
    global J_cost
    global D_cost
    global Demand
    global Config
    currentCapNW = float(Config["W.na"] * 180)
    currentCapEW = float(Config["W.eu"] * 180)
    currentCapAW = float(Config["W.ap"] * 180)
    currentCapNJ = float(Config["J.na"] * 450)
    currentCapEJ = float(Config["J.eu"] * 450)
    currentCapAJ = float(Config["J.ap"] * 450)
    currentCapND = float(Config["D.na"] * 1100)
    currentCapED = float(Config["D.eu"] * 1100)
    currentCapAD = float(Config["D.ap"] * 1100)

    projND = calcDemand("NA")
    projED = calcDemand("EU")
    projAD = calcDemand("AP")

    control = []
    #W.na
    control.append(int(math.ceil((projND - currentCapNW)/180)))
    #W.eu
    control.append(int(math.ceil((projED - currentCapEW)/180)))
    #W.ap
    control.append(int(math.ceil((projAD - currentCapAW)/180)))
    #J.na
    control.append(0)
    #J.eu
    control.append(0)
    #J.ap
    control.append(0)
    #D.na
    control.append(0)
    #D.eu
    control.append(0)
    #D.ap
    control.append(0)

    if (True):
        val = "CONTROL"
        for i in range(len(control)):
            val += " "
            val += str(control[i])
            #val += str(0)
        print val
        return val
        
def calcDemand(region):
    global Demand
    #doesn't start considering until we have at least 3 points
    if(len(Demand) < 3):
        return Demand[len(Demand) - 1][region]

    i = 0
    dx = Demand[len(Demand) - 1][region] - Demand[len(Demand) - 2][region]
    if(dx > 0):
        trend = "up"
    else:
        trend = "down"
    for m in xrange(len(Demand) - 2, 0, -1):
        i = i+1
        dx2 = Demand[i][region] - Demand[i - 1][region]
        if(dx > dx2):
            if(trend != "up"):
                return changeDemand(i, trend, region)
        if(dx < dx2):
            if(trend != "down"):
                return changeDemand(i, trend, region)

    return changeDemand(i, trend, region)

def changeDemand(i, trend, region):
    
    current = Demand[len(Demand) - 1][region]
    dx = Demand[len(Demand) - 1][region] - Demand[len(Demand) - 2][region]
    dx2 = Demand[len(Demand) - 2][region] - Demand[len(Demand) - 3][region]

    if(dx * dx2 < 0 and abs(dx) > 90):
        if(dx > 0):
            return current + int(1.125 * dx)
        else:
            return current - int(1.125 * dx)

    if(i == 1):
        return current

    if(i == 2):
        if(trend == "up"):
            return current + int(1.125 * dx)
        else:
            return current - int(1.125 * dx)

    if(i == 3):
        if(trend == "up"):
            return current + int(1.25 * dx)
        else:
            return current - int(1.25 * dx)

    if(i == 4):
        if(trend == "up"):
            return current + int(1.5 * dx)
        else:
            return current - int(1.5 * dx)

#parses demand data and stores it in global Demand
#global Demand will later be used to predict future demand
def parseDemand(data):
    global Demand
    demand = data.split()
    demand.pop(0)
    #if the length of Demand is > threshold, pop off the oldest data point
    if(len(Demand) >= 6):
        Demand.pop(0)
        Demand[0] = Demand[1]
        Demand[1] = Demand[2]
        Demand[2] = Demand[3]
        Demand[3] = Demand[4]
        Demand[4] = Demand[5]
        Demand[5] = {"NA": int(demand[4]), "EU": int(demand[5]), "AP": int(demand[6])}
    else:
        Demand[len(Demand)] = {"NA": int(demand[4]), "EU": int(demand[5]), "AP": int(demand[6])}  
       
#Pretty prints Demand
def printDemand():
    demandKeys = sorted(Demand.keys())
    for i in range (0, len(demandKeys)):
        print str(demandKeys[i]) + ": " + str(Demand[demandKeys[i]])

    print "length: " + str(len(Demand))

#Stores our current number of servers in each region into Config
def parseConfig(data):
    global Config
    config = data.split()
    config.pop(0)
    Config["W.na"] = int(config[0])
    Config["W.eu"] = int(config[1])
    Config["W.ap"] = int(config[2])
    Config["J.na"] = int(config[3])
    Config["J.eu"] = int(config[4])
    Config["J.ap"] = int(config[5])
    Config["D.na"] = int(config[6])
    Config["D.eu"] = int(config[7])
    Config["D.ap"] = int(config[8])
    

#Pretty prints a key-value pair in Config
#x is the tier.region you're looking for
#e.g. printConfig("W.na") prints the number of servers in the Web tier of North America
#case-sensitive
def printConfig(x):
    print x + ": " + Config[x]

#Pretty prints all key-value pairs in Config
def printAllConfig():
    configKeys = sorted(Config.keys())
    configKeys.reverse()
    for i in range(0,len(configKeys),3):
        print str(configKeys[i]) + ": " + str(Config[configKeys[i]]) + " \t" + str(configKeys[i+1]) + ": " + str(Config[configKeys[i+1]]) + " \t" + str(configKeys[i+2]) + ": " + str(Config[configKeys[i+2]])

def main():
    data = init()

    while (data != "END"):
#    for i in xrange(0,10):

        #print "---------------TURN# " + str(i) + "----------------"
        parseConfig(data)
        printAllConfig()
        s.send("RECD")
        #DEMAND
        data = s.recv(1024)
        print data
        parseDemand(data)
        printDemand()
#        if((i%100)==0):
#           global foo
#           foo.append((i,Demand[0]))

        s.send("RECD")
        #DIST
        data = s.recv(1024)
        print data
        s.send("RECD")
        #PROFIT
        data = s.recv(1024)
        print data
        s.send(move())
        print ""
        #CONFIG
        data = s.recv(1024)
        print data
    s.send("STOP")
    s.close()


main()
#print "foo: " + str(foo)

print "\nENDED"
