class Course:

    assigned = False
    prereqs = []
    avial = []

    # constructor
    def __init__(self, courseName, credits, prereqString):
            self.courseName = courseName
            self.credits = credits
            self.prereqString = prereqString
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
    """CS 260 [Min Grade: C] and (MATH 201 [Min Grade: C] or ENGR 231 [Min Grade: D])
     and (MATH 221 [Min Grade: C] or MATH 222 [Min Grade: C])
     and (MATH 311 [Min Grade: C] or MATH 410 [Min Grade: C] or ECE 361 [Min Grade: D])"""
     # o
     #patterns
     # () implies seperate sequence
    def preReqManip(string):
        pass

    def cleanPreqs(string):
        if Course.has_identifier(string):
            pass
            

    def has_identifier(inputString, identifier):
        if(identifier == "Digit"):
            return any(char.isdigit() for char in inputString)
        elif(identifier == "["):
            if identifier in inputString:
                return True
        elif(identifier == "&"):
            if identifier in inputString:
                return True
        elif(identifier == "|"):
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
        elif(identifier == "Elective"):
            if "elective" in inputString:
                return True
        else:
            return False


        

    