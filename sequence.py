class LinkedList:
    def __init__(self,head=None):
        self.head = head    

    def append(self, new_node):
        current = self.head
        if current:
            while current.next:
                current = current.next
            current.next = new_node
        else:
            self.head = new_node 

    def iterateThroughPrint(self):
        cur = self.head
        while(True):
            print(cur.data) #print the data
            if(cur.next is None): #this is our do-while loop emulation, checking if this is the last Node
                break
            
            if(cur.internalBool):
                print(" and ", end = "")
            else:
                print(" or ", end = "")
            cur = cur.next #update cur so we move on in the next iteration
    
    def iterateThroughSTR(self):
        cur = self.head
        string = ""
        while(True):
            string += cur.data #print the data
            if(cur.next is None): #this is our do-while loop emulation, checking if this is the last Node
                break
            
            if(cur.internalBool):
                string += " and "
            else:
                string += " or "
            cur = cur.next #update cur so we move on in the next iteration
        return string

    def delete(self, value):
        current = self.head
        if current.value == value:
            self.head = current.next
        else:
            while current:
                if current.value == value:
                    break
                prev = current
                current = current.next
            if current == None:
                return
            prev.next = current.next
            current = None   

    def insert(self, new_element, position):
            count=1
            current = self.head
            if position == 1:
                new_element.next = self.head
                self.head = new_element
            while current:
                if count+1 == position:
                    new_element.next =current.next
                    current.next = new_element
                    return
                else:
                    count+=1
                    current = current.next
class Node:    
    def __init__(self,data, internalBool = True):
        self.data = data
        """internal bool can be three values 0 for end, 1 for or, 2 for true
        internal bool other idea false = or, true =  and""" #<- current execution
        self.internalBool = internalBool    
        self.next = None
        

class Sequence:


    # CONSTRUCTOR
    def __init__(self, courses):
        self.courseArray = []
        if len(courses) < 10 and self.has_identifier(courses, "Digit"):
            l = LinkedList(Node(courses))
            self.courseArray.append(l)
        else:
            self.formatCourses(courses)

#--------------------------------------GETTERS/SETTERS-----------------------------   
     # returns an array of linked list where all indicies of array are ors
    def getSequence(self):
        return self.courseArray


#-------------------------------------FORMATS SEQUENCE-----------------------------
    # recursivly formats courses
    # splits by sequence and assumes sequence is or as positons in courseArray
    def formatCourses(self, courses):
        tempArray = []

        if (self.has_identifier(courses, "^")): #Looks for () ^ ()
            tempArray = courses.split("^") # turns into array of ()
            for val in tempArray: 
                self.formatCourses(val)    # sends individual ()
        elif (self.has_identifier(courses, "&")):
            tempArray = courses.split("&") # turns into array of inidivs 
            seq =  LinkedList(Node(tempArray[0], True)) #True for and
            del(tempArray[0]) #removes first entry since it was used to build array
            for val in tempArray:
                seq.append(Node(val, True)) #adds everything else to linkedlist
            self.courseArray.append(seq)
        elif (self.has_identifier(courses, "|")):
            tempArray = courses.split("|") # turns into array of inidivs 
            seq =  LinkedList(Node(tempArray[0], False))  #false for or
            del(tempArray[0]) #removes first entry since it was used to build array
            for val in tempArray:
                seq.append(Node(val, False)) #adds everything else to linkedlist
            self.courseArray.append(seq)
        else:
            seq = LinkedList(Node(courses))
            self.courseArray.append(seq)
    
#-------------------------------------FORMAT SEQUENCE HELPER METHOD-----------------------   
    # helper metheod
    def has_identifier(self, inputString, identifier):
        if(identifier == "Digit"):
            return any(char.isdigit() for char in inputString)
        elif identifier in inputString:
            return True        
        else:
            return False

   


#------------------------------------------PRINTING------------------------------
    def __str__(self):
        string = ""
        for i in range (len(self.courseArray)):
            string += self.courseArray[i].iterateThroughSTR()
            if i + 1 < len(self.courseArray):          
                string += "OR"
        return string

    # prints a formated version of the sequence
    def getFormatedSeqeuence(self):
        for course in self.courseArray:
            course.iterateThroughPrint()
            print("or")


