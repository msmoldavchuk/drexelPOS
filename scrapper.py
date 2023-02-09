import requests
from bs4 import BeautifulSoup
import pandas as pd
from course import Course as c
from sequence import Sequence as s, LinkedList, Node
from degree import Degree as d
# todo
# Get prequisite courses from the course catalog
#add course description to data frame
# format the prequisite courses into a list for each course(data frames)(michael)
#formating needs to be automated

#bonus todo 
#Parse the course catalog of all majors in a automated way

#step 2

#global variable
course_dictionary = {}
#creditsInWrongPlaceBoolean = False

#---------------------------------------METHODS TO SCRAPE DATA----------------------------------------
# This function takes in a course html and prints out the course id and name
def process_course_html(html_course):
    spacing_clauses = html_course.find('strong')

    
    course_id = spacing_clauses.contents[0].text.strip() #Obtains A Course ID In ABC 123 format 
    #course_name = spacing_clauses[1].contents.text.strip() #Does nothing temporarily
    course_credits = spacing_clauses.contents[2].text.strip() # Obtains a credit value range 0 to 4

   
    title = html_course.find_all("b", string = "Prerequisites:")
    temp = False
    prereqString = ""
    for child in html_course:
        if(temp): 
            prereqString = child #gets the pre requisetes in an unformated string
            break
        if child.text == "Prerequisites:":
            temp = True
# Create a course object w/ Course Id, Credits and UNFORMATED prereqstring
# Adds course object to dictonatiy w/ the key value being the course id
# i.e CS 172 maps to course object for CS 172 

    course_dictionary[course_id.replace("\xa0", " ")] = c(str(course_id), course_credits, prereqString)
   
def parseDegreeRequiremnts(degreename):
    degreelinks = {
        "CS": "https://catalog.drexel.edu/undergraduate/collegeofcomputingandinformatics/computerscience/#requirementsbstext", 
        "SE": "https://catalog.drexel.edu/undergraduate/collegeofcomputingandinformatics/softwareengineering/#degreerequirementstext", 
        "DS": "https://catalog.drexel.edu/undergraduate/collegeofcomputingandinformatics/datascience/#degreerequirementstext",
        "EDS": "https://catalog.drexel.edu/undergraduate/schoolofeconomics/economicsanddatascience/#degreerequirementstext",
        "CST": "https://catalog.drexel.edu/undergraduate/collegeofcomputingandinformatics/computingandsecuritytechnology/#degreerequirementstext",
        "IS": "https://catalog.drexel.edu/undergraduate/collegeofcomputingandinformatics/informationsystems/#degreerequirementstext"
    }
    
    degreelink = degreelinks[degreename]

    course_catalog = requests.get(degreelink).text
    parsed_course_catalog = BeautifulSoup(course_catalog, 'html.parser')
    course_list = parsed_course_catalog.find_all('table', class_='sc_courselist')

    degree_frame = pd.DataFrame()
    degree_frame = pd.read_html(str(course_list))[0]
    degree_frame.columns = ['Courses', 'Label', 'Credits']

    return degree_frame

#------------------------------------------METHODS TO CLEAN SCRAPPED DATA--------------------------------------

def parseThroughClasses(df):

    # turn columns of data frame into arrays
    courses = df.loc[:,'Courses']
    credits = df.loc[:,'Credits']

    #empty arrays to be filled during process and then turned into Dataframe
    coursesParsed = []
    creditsParsed = []
    descriptionsParsed = []
    flagParsed = [] # 0 = no problem, 1 = elective, 2 = choose, 3 = sequence, 4 = or

    # support vars for looping
    seqFlag = False
    descriptorRequired = ""
    inc = 1
    myiter = iter(range(0, len(courses)))
    strlength = 12 #temp value

    # use iter for sequence case
    for i in myiter:
        descriptorRequired = keyWordSearcher(courses[i], descriptorRequired) #step 1 check the type of course i.e cs or se

        if checkForNoCredits(credits[i]) and i >= 1:   #step 2 check if the credits exist if not then get previous
            credits[i] = credits[i-inc]
       
        if not seqFlag: # step 3 check if sequence mode
            # NOT A SEQUENCE

            if courses[i][0:2] == "or": # step 4 check if the course contains or
                # if it does then take the course previously added and then add current course
                """
                    EX:
                        CS 171
                        or CS 175
                        Replace "or" w/ "|"
                        Turn into one
                        CS 171 | CS 175
                """
                coursesParsed[len(coursesParsed)-1] = coursesParsed[len(coursesParsed)-1] + " | " + courses[i][3:len(courses[i])]
                descriptionsParsed[len(descriptionsParsed)-1] = descriptorRequired
                flagParsed[len(flagParsed)-1] = 4 #adds 4 for or flag
            elif len(courses[i]) <= strlength and has_identifier(courses[i], "Digit"): #step 5 check if the course is type ABC123
                coursesParsed.append(courses[i])
                creditsParsed.append(credits[i])
                descriptionsParsed.append(descriptorRequired)
                flagParsed.append(0)
            elif has_identifier(courses[i], "elective"): #step 6 check if the course has elective in it
                    flagParsed.append(1) #elective flag
                    if(has_identifier(courses[i], "Free")): #free electives = end of program
                        coursesParsed.append("Elective")
                        creditsParsed.append(credits[i]) 
                        descriptionsParsed.append("Special") #special internal descriptor
                    else: #not free elective then continue
                        coursesParsed.append("Elective") 
                        creditsParsed.append(credits[i])
                        descriptionsParsed.append(descriptorRequired)
            elif "sequences:" in courses[i]: #step 7 check if a sequence is comming up
                    seqFlag = True  # if yes change modes
        else: #step 4 sequence procedure activated 
            if ((len(courses[i]) <= strlength and has_identifier(courses[i], "Digit")) or has_identifier(courses[i], "&")): #step 5 look for courses
                coursesParsed.append(courses[i])
                creditsParsed.append(credits[i])
                flagParsed.append(0)
                descriptionsParsed.append(descriptorRequired)
            elif courses[i][0:2].lower() == "or": #step 6 look for or keyword *different than prior
                #Sequence ors get their own line
                i += 1 #skip current line and go to next one
                inc = 2  # ancounts for skip in line                                                    
                ns = str(coursesParsed[len(coursesParsed)-1]) + " ^ " + str(courses[i])         #take previous parsed and add to the new line    
                coursesParsed[len(coursesParsed)-1] = ns
                descriptionsParsed[len(descriptionsParsed)-1] = descriptorRequired
                flagParsed[len(flagParsed)-1] = 3                                        
                next(myiter, None) #iterates loop   
                """
                Sample
                Phys 101
                or
                Chem 101
                get to or and skip to chem 101
                Take phys 101 and combine w/ "^" in between
                """                                            
            elif has_identifier(courses[i], "elective"): #step 7 looks for electives
                coursesParsed.append("Elective")
                creditsParsed.append(credits[i])
                descriptionsParsed.append(descriptorRequired)
                flagParsed.append(1)
                seqFlag = False       # elective marks end of sequence         
            else:
                inc = 1
                seqFlag = False #emergancy way to end sequence
    # final step
    seqArray = []
    for course in coursesParsed:
        seqArray.append(s(course)) #convert filtered courses into array of sequence objects
    
    # make and return degree object
    return d(seqArray, creditsParsed, descriptionsParsed, flagParsed)    

#---------------------------------------------------HELPER METHODS FOR CLEANING DATA---------------------------------------

## paramater string to check and the indenitifier for the strong
## returns boolean value for if identifier is in string
def has_identifier(inputString, identifier):
    if(identifier == "Digit"):
        return any(char.isdigit() for char in inputString)
    elif identifier in inputString:
        return True
    else:
        return False

# displays data frame
# no return 

# Checks if a value has credits or is a pandas "nan" float
def checkForNoCredits(credit):
    if pd.notna(credit):
        return False
    else:
        return True


# searchers for a keyword
# returns descirptor based on key word
def keyWordSearcher(course, initialDescription):
    descriptor = initialDescription

    keyword_descriptor = {
        "Computer" : "CS",
        "Data": "DS", 
        "Software": "SE", 
        "Computing": "CI", 
        "Information": "IS", 
        "Science": "SCI", 
        "Mathematics":"MTH",
        "Arts & Humanities": "ArH", 
        "University": "Unv" 
    }

    if "Requirements" in course:
        for keyword in keyword_descriptor.keys():
            if keyword in course:
                return keyword_descriptor[keyword]
        descriptor = "None?"
                
    return descriptor

def convertPrereqsIntoCourses(course):
    tempArray = course.getPrereqArray()
    for tempP in tempArray:
        course_dictionary[str(tempP)]
    

#-----------------------------------------METHODS FOR DEBUGGING--------------------------------------------


def displayDF(df):
     with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(df)
        print("printed")          

def printList(list):
    for item in list:
        print(item)



if __name__ == '__main__':
    
    while True:
        try:
            #course_catalog = requests.get(input("Enter the course catalog: ")).text
            course_catalog = requests.get("https://catalog.drexel.edu/coursedescriptions/quarter/undergrad/cs/").text #gets website for cs
            if course_catalog == "":
                print("Empty URL try again")
                continue
            break
        except:
            print("Invalid URL try again")

    #html things
    parsed_course_catalog = BeautifulSoup(course_catalog, 'html.parser')
    course_list = parsed_course_catalog.find_all('div', class_='courseblock')

    # processes each entry
    for course in course_list:
        process_course_html(course)

    # ---------TESTING LINE-------------
        #prints the key pointing to a temp tostring for a course
        #below "prints" what pre reqs look like
    for key in course_dictionary:
       print(key + "->" + str(course_dictionary[key]))
       #course_dictionary[key].printPreqs()
    
    print(course_dictionary)
    print(str(course_dictionary["CS 385"]))

    NAME = "CS" # temp var
    
    ## modification ends
    cs_degree_frame = parseDegreeRequiremnts(NAME)
    #displayDF(cs_degree_frame)
    degreeReq = parseThroughClasses(cs_degree_frame)
    degreeReq.setDegreeName(NAME)
    print(degreeReq)


    
    
#------------------------------- EVERYTHING BELLOW IS TEMPORARLIY UNUSED PLEASE IGNORE----------------------------------------------
