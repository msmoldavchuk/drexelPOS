
"""
class Tree():
    def __init__(self,root):
        self.root = root
        self.children = []
    def addNode(self,obj):
        self.children.append(obj)

class Node():
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None
        self.children = []
    def addNode(self,obj):
        self.children.append(obj) 
""" 
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
                print(" and ")
            else:
                print(" or ")
            cur = cur.next #update cur so we move on in the next iteration

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
        #internal bool can be three values 0 for end, 1 for or, 2 for true
        #internal bool other idea false = or, true = and
        self.internalBool = internalBool    
        self.next = None
        

class Sequence:


    courseArray = []
    
    ## string not preformated
    # 1. Format string
    # 2. Make array
    def __init__(self, courses):
        
        if len(courses) < 10 and self.has_identifier(courses, "Digit"):
            l = LinkedList(Node(courses))
            self.courseArray.append(l)
        else:
            self.formatCourses(courses)
        

    
    def formatCourses(self, courses):
        tempArray = []

        if (self.has_identifier(courses, "^")):
            tempArray = courses.split("^")
            for val in tempArray:
                self.formatCourses(val)
        elif (self.has_identifier(courses, "&")):
            tempArray = courses.split("&")
            seq =  LinkedList(Node(tempArray[0]))
            del(tempArray[0])
            for val in tempArray:
                seq.append(Node(val, True))
            self.courseArray.append(seq)
        elif (self.has_identifier(courses, "|")):
            tempArray = courses.split("|")
            seq =  LinkedList(Node(tempArray[0]))
            del(tempArray[0])
            for val in tempArray:
                seq.append(Node(val, False))
            self.courseArray.append(seq)
        else:
            seq = LinkedList(Node(courses))
            self.courseArray.append(seq)
    
        

    def has_identifier(self, inputString, identifier):
        if(identifier == "Digit"):
            return any(char.isdigit() for char in inputString)
        elif(identifier == "&"):
            if identifier in inputString:
                return True
        elif(identifier == "|"):
            if identifier in inputString:
                return True
        elif(identifier == "^"):
            if identifier in inputString:
                return True
        elif(identifier == "Free"):
            if identifier in inputString:
                return True
        elif(identifier == "Elective"):
            if "elective" in inputString:
                return True
        else:
            return False

    def getSequence(self):
        return self.courseArray

    def getFormatedSeqeuence(self):
        for course in self.courseArray:
            course.iterateThroughPrint()
            print("or")



