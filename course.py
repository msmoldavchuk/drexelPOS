from sequence import LinkedList, Node
class Course:

    assigned = False
    
    avial = []
    #prereqArray = [] #index = and

    # constructor
    def __init__(self, courseName, credits, prereqString = "empty"):
            self.courseName = courseName
            self.credits = credits

            #normal assumption is that every index in prereq array is AND
            #if orboolean is true then every index in array is OR
            self.prereqArray = []
            self.orBoolean = False


            #makes sure prereq string is not none type
            if isinstance(prereqString, type(None)):
                self.prereqArray.append(False) 
            else:
                # clean and format the prerequiste string
                self.cleanPreqs(self.cleanCommas(self.concurentlyClear(self.cleanMinGrade(prereqString))))
                
   
            #self.avail = avail

    # getter for course name
    def getCourseName(self):
        return self.courseName
    
    # getter for credits
    def getCredits(self):
        return self.credits
    
    # getter pre reqs
    def getPrereqs(self):
        return self.prereqs
    
    # getter for availibility
    def getAvail(self):
        return self.avail
    
     # setter for courseName
    def setCourseName(self, courseName):
        self.courseName = courseName

    # setter for credits
    def setCredits(self, credits):
        self.credits = credits

    # setter for prereqs
    def setPrereqs(self, prereqs):
        self.prereqs = prereqs

    # setter for availibility
    def setAvial(self, avail):
        self.avail = avail
    
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

    # checks if a preq sequence has [(x and y) OR (a and b)] OR [(x or y) AND (a or b)]
    def inversalCheck(self, string):
        tempString = string
        if self.has_identifier(string, "("):
            tempString = string[string.index("(")+1:]
            if self.has_identifier(tempString, "("):
                tempString = tempString[tempString.index(")")-2:tempString.index("(")+2]               
                if self.has_identifier(tempString, "or"):
                    return True
                else:
                    return False
        return False

    # cleans a prequiste string and converts it into an array of linked lists
    def cleanPreqs(self, string):
        if self.inversalCheck(string): # (x and y) OR (a and b)
            self.orBoolean = True
            if (self.has_identifier(string, "or")):
                tempArray = string.split("or")
                for temp in tempArray:
                    if self.has_identifier(temp, "(") and self.has_identifier(temp, ")"): #linked list
                        orArray = temp[temp.index("(")+1:temp.index(")")].split("and")
                        linkedListArray =  LinkedList(Node(orArray[0], True))
                        del(orArray[0])
                        for orTemp in orArray:
                            linkedListArray.append(Node(orTemp, True))
                        self.prereqArray.append(linkedListArray)
                    else:
                        self.prereqArray.append(LinkedList(Node(temp)))
            else:        
                tempArray = string.split("and")
                linkedListArray =  LinkedList(Node(tempArray[0]))
                del(tempArray[0])
                for temp in tempArray:
                    linkedListArray.append(Node(temp, True))
                self.prereqArray.append(linkedListArray)
        else: # (x or y) AND (a or b)
            if (self.has_identifier(string, "and")):
                tempArray = string.split("and")
                for temp in tempArray:
                    if self.has_identifier(temp, "(") and self.has_identifier(temp, ")"): #linked list
                        orArray = temp[temp.index("(")+1:temp.index(")")].split("or")
                        linkedListArray =  LinkedList(Node(orArray[0], False))
                        del(orArray[0])
                        for orTemp in orArray:
                            linkedListArray.append(Node(orTemp, False))
                        self.prereqArray.append(linkedListArray)
                    else:
                        self.prereqArray.append(LinkedList(Node(temp)))
            else:        
                tempArray = string.split("or")
                linkedListArray =  LinkedList(Node(tempArray[0]))
                del(tempArray[0])
                for temp in tempArray:
                    linkedListArray.append(Node(temp, False))
                self.prereqArray.append(linkedListArray)
    
    # checks for x,y and if that exists replaces it w/ x and y
    def cleanCommas(self, string):
        if self.has_identifier(string, ","):
            return string.replace("," , " and")
        return string

    # removes "(Can be taken Concurrently)"
    def concurentlyClear(self, string):
        if self.has_identifier(string, "(Can be taken Concurrently)"):
            return string.replace("(Can be taken Concurrently)","")
        return string
            
    # removes the minimium grade from prereqs
    def cleanMinGrade(self, string):
        while(self.has_identifier(string, "[") or self.has_identifier(string, "]")):
            x = string[string.index('['):string.index(']')+1]
            string = string.replace(x,"")    
        return string
        

    #helper method that looks for a paramter keyword
    def has_identifier(self, inputString, identifier):
        if(identifier == "Digit"):
            return any(char.isdigit() for char in inputString)
        elif(identifier == "["):
            if identifier in inputString:
                return True
        elif(identifier == "]"):
            if identifier in inputString:
                return True
        elif(identifier == "&"):
            if identifier in inputString:
                return True
        elif(identifier == "|"):
            if identifier in inputString:
                return True
        elif(identifier == ","):
            if identifier in inputString:
                return True
        elif(identifier == "^"):
            if identifier in inputString:
                return True
        elif(identifier == "("):
            if identifier in inputString:
                return True
        elif(identifier == ")"):
            if identifier in inputString:
                return True
        elif(identifier == "and"):
             if identifier in inputString:
                return True
        elif(identifier == "or"):
            if identifier in inputString:
                return True
        elif(identifier == "(Can be taken Concurrently)"):
            if identifier in inputString:
                return True
        elif(identifier == "Elective"):
            if "elective" in inputString:
                return True
        else:
            return False


        

    