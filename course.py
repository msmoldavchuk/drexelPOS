from sequence import LinkedList, Node
import pandas as pd
class Course:

    
    
    #prereqArray = [] #index = and

    # constructor
    def __init__(self, courseName, credits, prereqString = "empty", avialabilityArray = [False, False, False, False], restrictionString = "None"):
            self.courseName = courseName.strip()
            self.credits = credits
            self.prereqString = prereqString

            #self.avialabilityArray = [False, False, False, False]
            
            self.avialabilityArray = avialabilityArray

            self.restrictionArray = []
            if restrictionString == "None":
                self.restrictionString = ""
            else:
                self.restrictionString = restrictionString
                self.restrictionArray = self.processRestrictionString(self.restrictionString)


            
            #normal assumption is that every index in prereq array is AND
            #if orboolean is true then every index in array is OR
            self.prereqArray = []
            
            self.orBoolean = False
            boolean = True
            self.andBoolean = boolean
            self.noPreqs = False

            self.mustAddBoolean = False
            self.seqCourse = []
            #makes sure prereq string is not none type
            if isinstance(prereqString, type(None)) or prereqString == "empty" or prereqString == "":
                self.prereqArray.append(LinkedList(Node(" "))) 
                self.noPreqs = True
                #print("Does this ever happen")
            else:
                # clean and format the prerequiste string
                self.cleanPreqs(self.wrongParanthesesCheck(self.cleanCommas(self.concurentlyClear(self.cleanMinGrade(prereqString)))))

                
   
            #self.avail = avail
    def getRestrctionString(self):
        return self.restrictionString
    
    # temp coded like this to hard filter data
    def processRestrictionString(self, string):
        finalArray = []
        if "Cannot enroll if classification is" in string:
            newString = string[string.find("Cannot enroll if classification is "):]
            newArray = newString.split("or")
            for part in newArray:
                arrayTwo = [part, False]
                finalArray.append(arrayTwo)
        return finalArray

    def processCannotEnroll(self):
        final = ""
        for classif in self.restrictionArray:
            final = classif[0]
        return final

    # improve in future    
    def processCourseRequirments(self, classif):
        if self.restrictionArray:       
            # cannot enroll
            if not self.restrictionArray[0][1]:
                if classif > self.convertClassifications(self.processCannotEnroll()):
                    return True
                else: return False
        else:
            return True
        
    def convertClassifications(self, string):
        if string.strip() == "Senior":
            return 5
        elif string.strip() == "Junior":
            return 4
        elif string.strip() == "Pre-Junior":
            return 3
        elif string.strip() == "Sophmore":
            return 2
        else:
            return 1
        
    def getPrereqArray(self):
        return self.prereqArray

    def appendToPreReqArray(self, val):
        self.prereqArray.append(val)

    def setAviabilityTrue(self, index):
        self.avialabilityArray[index] = True
#---------------------------------------GETTERS/SETTERS-----------------------------------
    
    # getter for course name
    def getCourseName(self):
        return self.courseName
    
    # getter for credits
    def getCredits(self):
        return float(self.credits)

    def getAndBoolean(self):
        return self.andBoolean
    
    def getPrereqString(self):
        return self.prereqString

    def getFallAvail(self)->bool:
        return self.avialabilityArray[0]

    def getWinterAvail(self)->bool:
        return self.avialabilityArray[1]

    def getSpringAvail(self)->bool:
        return self.avialabilityArray[2]

    def getSummerAvail(self)->bool:
        return self.avialabilityArray[3]  
        
     # setter for courseName
    def setCourseName(self, courseName):
        self.courseName = courseName

    # setter for credits
    def setCredits(self, credits):
        self.credits = credits

    def setAndBoolean(self, paramater):
        self.andBoolean = paramater

    def getAvial(self):
        return self.avialabilityArray

    def createSequence(self, course):
        #print(self.getCourseName() + " then " + course.getCourseName())
        self.seqCourse.append(course)
    
    def setMustAddBoolean(self, bool):
        self.mustAddBoolean = bool

    def getMustAddBoolean(self):
        return self.mustAddBoolean
    def checkIfSequence(self):
        if not self.seqCourse:
            return False
        else:
            return True
    def checkSequenceLength(self):
        if self.checkIfSequence():
            return 1 + self.seqCourse[0].checkSequenceLength()
        return 0
    
    def adjustSequencePriority(self):
        if self.checkIfSequence():
            self.seqCourse[0].setMustAddBoolean(True)

    def findMissingPrereq(self, df:pd.DataFrame):
        #print(self.getCourseName())

        if self.getAndBoolean(): #normal  ((x or y) and (a or b))
            for prereqSequence in self.getPrereqArray():
                if not prereqSequence.checkDataFrame(df): 
                    courses = prereqSequence.iterateThroughArray()
                    for course in courses:
                        if not (course in df.loc[:,"Courses"].tolist()):
                            return course
        else: #((x and y) or (a and b)) NOT TESTED FULLY!!!!!!!!
            for prereqSequence in self.getPrereqArray():
                courses = prereqSequence.iterateThroughArray()
                for course in courses:
                    if not (course in df.loc[:,"Courses"].tolist()):
                            return course


    
        
#-------------------------------------------------CONVERTS PREREQS--------------------------------------
    # cleans a prequiste string and converts it into an array of linked lists
    def cleanPreqs(self, string):
        if self.inversalCheck(string): # step 1 check for (x and y) OR (a and b)
            #print("1")
            self.setAndBoolean(False) #makes it so that every index of array means or not and
            if (self.has_identifier(string, "or")):  # step 2 splits on or
                tempArray = string.split("or")
                for temp in tempArray:
                    if self.has_identifier(temp, "(") and self.has_identifier(temp, ")"): #step 3 look for ()
                        orArray = temp[temp.index("(")+1:temp.index(")")].split("and") #step 4 split () on "AND" after removing ()
                        linkedListArray =  LinkedList(Node(orArray[0].strip(), True))
                        del(orArray[0])
                        for orTemp in orArray:
                            linkedListArray.append(Node(orTemp.strip(), True)) # step 6 add to linked list w/ and internal
                        self.appendToPreReqArray(linkedListArray)
                    else:
                        
                        self.appendToPreReqArray(LinkedList(Node(temp.strip(), True)))
            else:        
                tempArray = string.split("and") #indiv seperate on and
                linkedListArray =  LinkedList(Node(tempArray[0].strip(), True))
                del(tempArray[0])
                for temp in tempArray:
                    linkedListArray.append(Node(temp.strip(), True))
                self.appendToPreReqArray(linkedListArray)
        else: # step 1.5 go w/ (x or y) AND (a or b)
            self.setAndBoolean(True) #makes it so that every index of array means or not and
            if (self.has_identifier(string, "and")): # step 2 splits on and
                tempArray = string.split("and") 
                for temp in tempArray:
                    if self.has_identifier(temp, "(") and self.has_identifier(temp, ")"):  #step 3 look for ()
                        orArray = temp[temp.index("(")+1:temp.index(")")].split("or") #step 4 split () on "OR" after removing ()
                        linkedListArray =  LinkedList(Node(orArray[0].strip(), False))
                        del(orArray[0])
                        for orTemp in orArray:
                            linkedListArray.append(Node(orTemp.strip(), False)) # step 6 add to linked list w/ or internal
                        self.appendToPreReqArray(linkedListArray)
                    else:
                        self.appendToPreReqArray(LinkedList(Node(temp.strip(), False)))
            elif self.has_identifier(string, "or"):        
                tempArray = string.split("or")
                """if tempArray[0].strip() == "MATH 117":
                    print("HERE")
                    print(self.getCourseName())"""
                linkedListArray =  LinkedList(Node(tempArray[0].strip(), False))
                del(tempArray[0])
                for temp in tempArray:
                    linkedListArray.append(Node(temp.strip(), False))
                self.appendToPreReqArray(linkedListArray)
            else:
                
                """if string.strip() == "ENGL 101":
                    print("OR")
                    print(self.getCourseName())"""
                
                self.appendToPreReqArray(LinkedList(Node(string.strip(), False)))

#-----------------------------------------CLEANS PREREQS(HELPER METHODS)------------------------------
    
    # checks if a preq sequence has [(x and y) OR (a and b)] OR [(x or y) AND (a or b)]
    def inversalCheck(self, string)->str:
        tempString = string
        if self.has_identifier(string, "("):
            tempString = string[string.index("(")+1:]
            if self.has_identifier(tempString, "("):
                tempString = tempString[tempString.index(")")-2:tempString.index("(")+2]               
                if self.has_identifier(tempString, "or"):
                    return True
                else:
                    return False
            elif self.has_identifier(tempString, ")"): # 10 is a magic number
                #print("This course made it here " + string)
                string = string[string.index("(")-6:string.index("(")]
                #print("\t w/ tempString: " + string)
                if self.has_identifier(string, "or"):
                    return True
                else:
                    return False
        return False

    # checks for x,y and if that exists replaces it w/ x and y
    def cleanCommas(self, string)->str:
        if self.has_identifier(string, ","):
            return string.replace("," , " and")
        return string

    # removes "(Can be taken Concurrently)"
    def concurentlyClear(self, string)->str:
        if self.has_identifier(string, "(Can be taken Concurrently)"):
            return string.replace("(Can be taken Concurrently)","")
        return string
            
    # removes the minimium grade from prereqs
    def cleanMinGrade(self, string)->str:
        while(self.has_identifier(string, "[") or self.has_identifier(string, "]")):
            x = string[string.index('['):string.index(']')+1]
            string = string.replace(x,"")    
        return string
    
    def wrongParanthesesCheck(self, string)->str:
        if self.has_identifier(string, "(") and not self.has_identifier(string, ")"):
            string = string.replace("(","")
        elif self.has_identifier(string, ")") and not self.has_identifier(string, "("):
            string = string.replace(")","")
        return string

    #helper method that looks for a paramter keyword
    def has_identifier(self, inputString, identifier)->str:
        if(identifier == "Digit"):
            return any(char.isdigit() for char in inputString)
        return (identifier in inputString)

    def havePreqs(self, df: pd.DataFrame):
        if self.noPreqs:
            return True
        elif self.getAndBoolean():
            for prereqSequence in self.getPrereqArray():
                andBooleanInternal = False
                if prereqSequence.checkDataFrame(df):
                    andBooleanInternal = True
                if andBooleanInternal == False:
                    return False
            return True
        else:
            for prereqSequence in self.prereqArray:
                if prereqSequence.checkDataFrame(df):
                    return True              
        return False
#--------------------------------------------PRINTING------------------------------------

     #temp toString
    def __str__(self):
        return "Course: " + self.courseName

    def printPreqs(self):
        for prereq in self.prereqArray:
            prereq.iterateThroughPrint()
            if self.orBoolean:
                print(" or ", end = "")
            else:
                print(" and ", end = "")