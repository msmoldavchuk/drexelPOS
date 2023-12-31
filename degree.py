from sequence import Sequence as s
import pandas as pd
import random
import csv
from ast import literal_eval 
# flags
# 3 = seq
# 6 = select
# 9 = handeled


class Degree():
    # constructor for degree object
    # recives arrays and converts them into a dataframe
    
    def __init__(self, seq = [], credit = [], descriptor = [], flag = [], num = [], concList: list = [], concCredits:float = 0,requiredConcentration = False, requiredMinor = False):
        self.degreeFrame = pd.DataFrame({"Sequence": seq, "Credits": credit, "Type": descriptor, "Flag": flag, "Num": num, "Taken": False})
        self.degreeName = ""
        self.degreeCollege = ""

        
            
        self.concentrationsList = concList
        self.concentrationCredits = concCredits
        self.requiredConcentration = requiredConcentration
        self.requiredMinor = requiredMinor
        self.fullDegree = self.degreeFrame

        self.freeElectiveMode = True
        
        #self.electiveDictonary = {} implemant latter w/ scrapping

    def getFreeElectiveMode(self):
        return self.freeElectiveMode
    
    def freeElectivesRandom(self):
        if self.getFreeElectiveMode():
            for i in range(len(self.degreeFrame.index)):
                if self.degreeFrame.loc[i,"Type"] == "Special":
                    
                    if random.randint(1,4) == 4:
                        credit = 4
                        self.degreeFrame.loc[i,"Credits"] = str(float(self.degreeFrame.loc[i,"Credits"]) - credit)
                        if float(self.degreeFrame.loc[i,"Credits"]) == -1:
                            credit = 3
                            self.degreeFrame.loc[i,"Credits"] = str(float(self.degreeFrame.loc[i,"Credits"]) - credit)
                            self.freeElectiveMode = False
                        elif float(self.degreeFrame.loc[i,"Credits"]) <= 0:
                            self.freeElectiveMode = False
                    else:
                        credit = 3
                        self.degreeFrame.loc[i,"Credits"] = str(float(self.degreeFrame.loc[i,"Credits"]) - credit)
                        if float(self.degreeFrame.loc[i,"Credits"]) == 1:
                            credit = 4
                            self.degreeFrame.loc[i,"Credits"] = str(float(self.degreeFrame.loc[i,"Credits"]) - credit)
                            self.freeElectiveMode = False
                        elif float(self.degreeFrame.loc[i,"Credits"]) <= 0:
                            self.freeElectiveMode = False
                    return ["Free Elective" , credit]
        else:
            return ["No Class" , 0]
        return ["No Class", 0]

    
    def convertDegreeToCSV(self, name):
        self.degreeFrame.to_csv(name+ "Degree.csv",index=False)
        if self.requiredConcentration:
            for i in range(len(self.concentrationsList[1])):
                try:
                    if self.concentrationsList[0][i].loc[1,"Sequence"] != "": #makes sure df isn't empty
                        self.concentrationsList[0][i].to_csv(name + "Concentrations" + str(i) + ".csv", index = False)
                except:
                    pass


    def convertCSVToDegree(self, name):
        df = pd.read_csv(name + "Degree.csv",converters={3:literal_eval})
        df.columns = ['Sequence', 'Credits', 'Type', "Flag","Num", "Taken"]
        for i in range(len(df.index)):
            df.loc[i,"Sequence"] = s(df.loc[i,"Sequence"])
        self.degreeFrame = df
        self.concentrationsList = [[],[]]
        existenceIndex = -1
        try:
            for i in range(1,9999):
                concentrationDf = pd.read_csv(name + "Concentrations" + str(i) + ".csv",converters={3:literal_eval})
                concentrationDf.columns = ['Sequence', 'Credits', 'Type', "Flag", "Num", "Taken"]
                for j in range(len(concentrationDf.index)):
                    concentrationDf.loc[j,"Sequence"] = s(concentrationDf.loc[j,"Sequence"])
               
                self.concentrationsList[0].append(concentrationDf)
                self.concentrationsList[1].append(concentrationDf.loc[1,"Type"])
                existenceIndex = i
        except:
            if existenceIndex == -1:
                self.concentrationsList = [[],[]]
                self.requiredConcentration = False
            else:
                self.requiredConcentration = True
        self.fullDegree = df



    def checkCompletion(self, df:pd.DataFrame): 
        for i in range(len(self.degreeFrame.index)):
            if self.degreeFrame.loc[i, "Taken"] == False:
                sequences = self.degreeFrame.loc[i, "Sequence"].getSequence()
                for seq in sequences: # if anything meets all reqs then the sequence is complete move on to next sequence
                    if seq.checkDataFrame(df):
                        self.degreeFrame.loc[i, "Taken"] = True
                        break
        #self.displayDF(df) # test line
                
    def checkIfTaken(self, course):
        for i in range(len(self.degreeFrame.index)):
            sequences = self.degreeFrame.loc[i, "Sequence"].getSequence()
            for seq in sequences:
                if seq.checkIfContains(course):
                    return self.degreeFrame.loc[i, "Taken"]
        return False

    def takeFreeElectives(self, credits):
         for i in range(len(self.degreeFrame.index)):
            if self.degreeFrame.loc[i,"Type"] == "Special":
                self.degreeFrame.loc[i,"Credits"] = str(float(self.degreeFrame.loc[i,"Credits"]) - credits)
                break

    def printConcentrations(self):
        for i in range(len(self.concentrationsList[1])):
            try:
                desc = self.concentrationsList[1][i]
                print(str(desc)+ " Concentration")
                self.displayDF(self.concentrationsList[0][i])
            except:
                pass


    def displayDF(self, df):
     with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(df)
        print("printed")        

    def displayDFMain(self):
        self.displayDF(self.degreeFrame)

    def seperateConcentrations(self, concList):
        finalArray = []
        changeIndex = 0
        for concentration in concList:
            descriptions = concentration[2]
            pastDescription = descriptions[0]
            for i in range(len(descriptions)):
                if pastDescription != descriptions[i]:
                    finalArray.append([concentration[0][changeIndex:i], concentration[1][changeIndex:i], concentration[2][changeIndex:i], concentration[3][changeIndex:i]])
                    changeIndex = i
                pastDescription = descriptions[i]
            finalArray.append([concentration[0][changeIndex:], concentration[1][changeIndex:], concentration[2][changeIndex:], concentration[3][changeIndex:]])
        return finalArray

    #CLEAN LATER
    def selectConcentration(self, choice, courses):
        pos = 0
        for i in range(len(self.concentrationsList[1])):
            if self.concentrationsList[1][i] == choice:
                pos = i
                break
        
        x = self.concentrationsList[0][pos] 
        for i in range(len(x.index)):
            if str(x.loc[i, "Sequence"]) in courses:
                self.addToFullDegreeSeries(x.loc[i])
        #self.displayDF(x)
        #return x
    


    def addToFullDegreeDf(self, new):
        for i in range(len(new.index)): 
            if not (new.loc[i, "Sequence"] in self.fullDegree.loc[:,"Sequence"].tolist()):
                self.fullDegree.loc[len(self.fullDegree.index)] = new.loc[i, "Sequence"]
        #self.displayDF(self.fullDegree)
    
    def addToFullDegreeSeries(self, new): 
        if not (new[0] in self.fullDegree.loc[:,"Sequence"].tolist()):
            self.fullDegree.loc[len(self.fullDegree.index)] = new
        #self.displayDF(self.fullDegree)

    def getFullDegree(self):
        return self.fullDegree
    
    def userChooseCourse(self, arrayOfChoice, dictonary):
        for selection in arrayOfChoice:
            for i in range(len(self.degreeFrame.index)):
                if self.degreeFrame.loc[i,"Flag"] == 3:
                    if self.degreeFrame.loc[i,"Type"] == "SCI":
                        self.selectScienceSequence(selection, dictonary)
                    else:
                        self.sequenceNumberSystem(selection, dictonary)
                elif self.degreeFrame.loc[i,"Flag"] == 6:
                    self.selectCourseList(selection)
    
    def sequenceNumberSystem(self, choice, dictonary):
        if type(choice) == int: 
            for i in range(len(self.degreeFrame)):
                if self.degreeFrame.loc[i, "Flag"] == 3:
                    
                    seqs = self.degreeFrame.loc[i, "Sequence"].getSequence()
                    self.degreeFrame.loc[i, "Sequence"] = s(seqs[choice])
                    credits = 0.0
                    seqsTwo = seqs[choice].iterateThroughArray()
                    for seqTwo in seqsTwo:
                        credits += dictonary[seqTwo.strip()].getCredits()
                    self.degreeFrame.loc[i, "Credits"] = str(credits)
                    self.degreeFrame.loc[i,"Flag"] = 9
                    self.setPostCredits(i)
                    break
                    

    # MASON READ THIS
    # Returns an array containting arrays
    # the sub arrays either contain
    #   [Sequence object, Type(integer), number needed]
    # or
    #   [list of concentrations] (each item in the list is a dataframe and you want to display all the courses in the data frame)                
    def getDataForWebsite(self):
        dataArray = []
        for i in range(len(self.degreeFrame.index)):
            if self.degreeFrame.loc[i,"Flag"] == 3:
                if self.degreeFrame.loc[i,"Type"] == "SCI":
                    dataArray.append([self.degreeFrame.loc[i,"Sequence"],self.degreeFrame.loc[i,"Type"],self.degreeFrame.loc[i,"Num"]])
            elif self.degreeFrame.loc[i,"Flag"] == 6:
                dataArray.append([self.degreeFrame.loc[i,"Sequence"],self.degreeFrame.loc[i,"Type"],self.degreeFrame.loc[i,"Num"]])
        if self.requiredConcentration:
            dataArray.append([self.concentrationsList])
        return dataArray


    def selectCourseList(self, choiceSet):
        newSeqSubset = ""
        for i in range(len(self.degreeFrame)):
            if self.degreeFrame.loc[i, "Flag"] == 6:
                for seqs in self.degreeFrame.loc[i, "Sequence"].getSequence():
                    seq = seqs.iterateThroughArray()
                    for course in seq:
                        if course.strip() in choiceSet:
                            if newSeqSubset == "":
                                newSeqSubset = course
                            else:
                                newSeqSubset += " & " + course
                if newSeqSubset != "":
                    self.degreeFrame.loc[i, "Sequence"] = s(newSeqSubset)
                    self.degreeFrame.loc[i,"Flag"] = 9
                    break
                    

    def selectScienceSequence(self, choice, dictonary):
        if type(choice) == str: 
            for i in range(len(self.degreeFrame)):
                if self.degreeFrame.loc[i, "Type"] == "SCI" and self.degreeFrame.loc[i, "Flag"] == 3:
                    for seqs in self.degreeFrame.loc[i, "Sequence"].getSequence():
                        seq = seqs.iterateThroughArray()
                        #print(seq)
                        if self.has_identifier(seq[0], choice):
                            self.degreeFrame.loc[i, "Sequence"] = s(seqs)
                            credits = 0.0
                            seqsTwo = seqs.iterateThroughArray()
                            for seqTwo in seqsTwo:
                                credits += dictonary[seqTwo.strip()].getCredits()
                            self.degreeFrame.loc[i, "Credits"] = str(credits)
                            self.degreeFrame.loc[i,"Flag"] = 9
                            self.setPostCredits(i)
                            break


    # returns credits for a specfic sequence
    def getCredit(self, seq):
        self.degreeFrame[self.degreeFrame[s]==[seq].index]

        return self.credit

    # returns a specgic sequence
    def getSpecficSeq(self, seq):
        return self.degreeFrame[self.degreeFrame[s]==[seq]]
    
    # returns a sequence at a specfic index
    def getSeqAt(self, index):
        return self.degreeFrame.loc[index, "Sequence"]

    # returns dataframe
    def getDegree(self):
        return self.degreeFrame

    # gets the length of the data frame
    def getLength(self):
        return len(self.degreeFrame.index)

    #gets the name for the degree
    def getDegreeName(self):
        return self.degreeName

    # sets the name for the degree
    def setDegreeName(self, name):
        self.degreeName = name

     #gets the name for the degree
    def getDegreeCollege(self):
        return self.degreeCollege

    def getTaken(self, course):
        for i in range(len(self.degreeFrame.index)):
            sequence = self.degreeFrame.loc[i, "Sequence"]
            seqArray = sequence.getSequence()
            for seq in seqArray:
                if seq.checkIfContains(course.split()):
                    return self.degreeFrame.loc[i, "Taken"]

    # sets the name for the degree
    def setDegreeCollege(self, col):
        self.degreeCollege = col


    def getConcentrationsTesting(self):
        return self.concentrationsList
    
    def getElectives(self):
        electiveDataFrame = pd.DataFrame({"Sequence": [], "Credits": [],"Type": [], "Flag":[], "Taken": []})
        for i in range(len(self.degreeFrame.index)):
            if self.degreeFrame.loc[i, "Flag"] == 1:
                electiveDataFrame.loc[len(electiveDataFrame.index)] = self.degreeFrame.loc[i]
        return electiveDataFrame
    
    def pickElectiveRandom(self):
        for i in range(len(self.degreeFrame.index)):
            if self.degreeFrame.loc[i, "Flag"] == 1 and self.degreeFrame.loc[i,"Type"] != "Special" and self.degreeFrame.loc[i,"Taken"] == False:
                elective = self.degreeFrame.loc[i,"Type"] + " " + str(self.degreeFrame.loc[i, "Sequence"])
                if "science" in elective:
                    credit = 4.0
                else:
                    credit = 3.0
                #print(elective)
                self.degreeFrame.loc[i,"Credits"] = str(float(self.degreeFrame.loc[i,"Credits"]) - credit)
                if float(self.degreeFrame.loc[i, "Credits"]) < 0:
                    counter = 0
                    while float(self.degreeFrame.loc[i, "Credits"]) < 0:
                        self.degreeFrame.loc[i, "Credits"] = str(float(self.degreeFrame.loc[i, "Credits"]) + 1)
                        counter += 1
                    self.takeFreeElectives(counter)
                    
                
                if float(self.degreeFrame.loc[i,"Credits"]) == 0:
                    self.degreeFrame.loc[i,"Taken"] = True

                return [elective, credit]
            elif self.degreeFrame.loc[i, "Flag"] == 1 and self.degreeFrame.loc[i,"Type"] == "Special":
                self.freeElectiveMode = True
                return ["No Class", 0]
        return ["No Class", 0]

    def setPostCredits(self, index):
        self.degreeFrame.loc[index + 1, "Credits"] = str(float(self.degreeFrame.loc[index+1, "Credits"]) - float(self.degreeFrame.loc[index, "Credits"]))

    # to string for the degree
    def __str__(self):
        type = ""
        string = ""
        print(self.getDegreeName() + " Degree: ")
        for i in range(self.getLength()):
            if not(self.degreeFrame.loc[i, "Type"] == type): # if the type changes then print the new type i.e if moving from cs to se courses
                type = self.degreeFrame.loc[i, "Type"]
                string += type + " Requirements\n"
                if self.degreeFrame.loc[i, "Type"] == "Special": # condtion for free elctives and degree requiremnts
                    string += "\tFree Elective: " + str(self.degreeFrame.loc[i, "Credits"]) + " Credits Needed\n"
                    string += "\tTotal Credits: "  + str(self.degreeFrame.loc[i+1, "Credits"]) + " Credits Needed\n"
                    break
            
            if  self.degreeFrame.loc[i, "Flag"] == 1: #if the item is an elective then it gets a special print
                string += "\t" + self.degreeFrame.loc[i, "Type"] + " Elective: " + str(self.degreeFrame.loc[i, "Credits"]) + " Credits Needed\n"               
            else: #otherwise prints the sequence
                #string += "\tCourse: " + str(self.degreeFrame.loc[i, "Sequence"])+"\tCredits: " + str(self.degreeFrame.loc[i, "Credits"]) + "\n" #temp unused cause ugly
                string += "\tCourse: " + self.degreeFrame.loc[i, "Sequence"].printFormating()+"\n"

        return string
    
    def has_identifier(self, inputString, identifier)->str:
        if(identifier == "Digit"):
            return any(char.isdigit() for char in inputString)
        return (identifier in inputString)











