from sequence import Sequence as s
import pandas as pd

class Degree():
    # constructor for degree object
    # recives arrays and converts them into a dataframe
    
    def __init__(self, seq, credit, descriptor, flag, concDF = pd.DataFrame(), concCredits:float = 0):
        self.degreeFrame = pd.DataFrame({"Sequence": seq, "Credits": credit, "Type": descriptor, "Flag": flag, "Taken": False})
        self.degreeName = ""
        self.degreeCollege = ""

        
            
        self.concentrationsDF:pd.DataFrame = concDF
        self.concentrationCredits = concCredits
        
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


    def printConcentrations(self):
        for i in range(len(self.concentrationsDF.loc[:,"Concentration"])):
            desc = self.concentrationsDF.loc[i,"Name"] 
            print(str(desc)+ " Concentration")
            self.displayDF(self.concentrationsDF.loc[i,"Concentration"])

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
    def selectConcentration(self, choice):
        pos = 0
        for i in range(len(self.concentrationsDF.loc[:,"Name"])):
            if self.concentrationsDF.loc[i,"Name"] == choice:
                pos = i
                break

        x =self.concentrationsDF.loc[pos, "Concentration"]
        #self.displayDF(x)
        return x

    def selectScienceSequence(self, choice):
        for i in range(len(self.degreeFrame)):
            if self.degreeFrame.loc[i, "Type"] == "SCI" and self.degreeFrame.loc[i, "Flag"] == 3:
                for seqs in self.degreeFrame.loc[i, "Sequence"].getSequence():
                    seq = seqs.iterateThroughArray()
                    #print(seq)
                    if self.has_identifier(seq[0], choice):
                        #print("DOES THIS OCCUR!!!!!!!!!!!!!!!!")
                        self.degreeFrame.loc[i, "Sequence"] = s(seqs)
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

    def getMegaDegreeRequirments(self):
        #tempDataFrame = self.degreeFrame.append(self.concentrationsDF)
        tempDataFrame = pd.concat([self.degreeFrame, self.concentrationsDF],axis = 1)
        return tempDataFrame

    
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
                string += "\tCourse: " + str(self.degreeFrame.loc[i, "Sequence"])+"\n"

        return string
    
    def has_identifier(self, inputString, identifier)->str:
        if(identifier == "Digit"):
            return any(char.isdigit() for char in inputString)
        return (identifier in inputString)

    