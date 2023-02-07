import requests
from bs4 import BeautifulSoup
import pandas as pd
from course import Course as c
from sequence import Sequence as s
# todo
# Get prequisite courses from the course catalog
#add course description to data frame
# format the prequisite courses into a list for each course(data frames)(michael)
#formating needs to be automated

#bonus todo 
#Parse the course catalog of all majors in a automated way

#step 2

#global variable
course_list_all = []
course_dictionary = {}

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
    course_dictionary[course_id] = c(course_id, course_credits, prereqString)
   

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
       course_dictionary[key].printPreqs()

    
    
#------------------------------- EVERYTHING BELLOW IS TEMPORARLIY UNUSED PLEASE IGNORE----------------------------------------------


## paramater string to check and the indenitifier for the strong
## returns boolean value for if identifier is in string
def has_identifier(inputString, identifier):
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

# displays data frame
# no return 
def displayDF(df):
     with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(df)
        print("printed")

# parses through a degree dataframe (paramter) 
# returns dataframe of parsed data
def parseThroughClasses(df):
    courses = df.loc[:,'Courses']
    credits = df.loc[:,'Credits']
    coursesParsed = []
    creditsParsed = []
    descriptionsParsed = []
    flagParsed = [] # 0 = no problem, 1 = elective, 2 = choose, 3 = sequence, 4 = or
    seqFlag = False
    descriptorRequired = ""
    myiter = iter(range(0, len(courses)))
    for i in myiter:
        descriptorRequired = keyWordSearcher(courses[i], descriptorRequired)
        if seqFlag == True:
            if ((len(courses[i]) <= 10 and has_identifier(courses[i], "Digit")) or has_identifier(courses[i], "&")):
                #coursesParsed.append(courses[i])
                #creditsParsed.append(credits[i])
                course = c(courses[i], credits[i]) #c
                coursesParsed.append(course)
                flagParsed.append(0)
                descriptionsParsed.append(descriptorRequired)
            elif courses[i][0:2].lower() == "or":
                i += 1
                ns = coursesParsed[len(coursesParsed)-1] + " ^ " + courses[i]
                coursesParsed[len(coursesParsed)-1] = ns
                descriptionsParsed[len(descriptionsParsed)-1] = descriptorRequired
                flagParsed[len(flagParsed)-1] = 3
                next(myiter, None)
            elif has_identifier(courses[i], "Elective"):
                coursesParsed.append("Elective")
                creditsParsed.append(credits[i])
                descriptionsParsed.append(descriptorRequired)
                flagParsed.append(1)
                seqFlag = False                
            else:
                seqFlag = False 
        else:               
            if courses[i][0:2].lower() == "or": 
                ns = coursesParsed[len(coursesParsed)-1] + " | " + courses[i][3:len(courses[i])]
                coursesParsed[len(coursesParsed)-1] = ns
                descriptionsParsed[len(descriptionsParsed)-1] = descriptorRequired
                flagParsed[len(flagParsed)-1] = 4
            elif len(courses[i]) <= 10 and has_identifier(courses[i], "Digit"):
                course = c(courses[i], credits[i]) # c
                coursesParsed.append(course)
                descriptionsParsed.append(descriptorRequired)
                flagParsed.append(0)
            elif has_identifier(courses[i], "Elective"):
                flagParsed.append(1)
                if(has_identifier(courses[i], "Free")):
                    coursesParsed.append("Elective")
                    creditsParsed.append(credits[i]) 
                    descriptionsParsed.append("Special")
                else:
                    coursesParsed.append("Elective")
                    creditsParsed.append(credits[i])
                    descriptionsParsed.append(descriptorRequired)
            elif "sequences:" in courses[i]:
                seqFlag = True       
    tempDF = pd.DataFrame({"Courses": coursesParsed,"Type": descriptionsParsed, "Assigned": False, "Flag": flagParsed})
    return tempDF

# displays a degree
# paramaters are parsedDataFrame and name of degree
def displayDegree(df, degreeName):
    type = ""
    print(degreeName + " Degree:")
    for i in range(len(df.index)):
        if not(df.loc[i, "Type"] == type):
            type = df.loc[i, "Type"]
            print(type + " Requirements") 
            if df.loc[i, "Type"] == "Special":
                print("\tFree Elective: " + str(df.loc[i, "Credits"]) + " Credits Needed")
                break
                
        if  df.loc[i, "Courses"] == "Elective":
            print("\t" + df.loc[i, "Type"] + " Elective: " + str(df.loc[i, "Credits"]) + " Credits Needed")
        else:
            if df.loc[i, "Flag"] == 0:
                print("\tCourse: " + df.loc[i, "Courses"])
            elif df.loc[i, "Flag"] == 4:
                print("\tCourse: " + splicerPrintPrep(df.loc[i, "Courses"]))
            elif df.loc[i, "Flag"] == 3:
                sequencePrint(df.loc[i, "Courses"])

# returns a modified string for printing
def splicerPrintPrep(word):
    if has_identifier(word, "|"):
        return word.replace("|", " or ")
    elif has_identifier(word, "&"):
        return word.replace("&", " and ")
    else:
        return ""
    
        
# printing method for sequences
def sequencePrint(word):
    i = 1
    if has_identifier(word, "^"):
        seqs = word.split("^")
        print("Sequence Choose 1: ")
        for seq in seqs:
            print("\t"+str(i)+"."+splicerPrintPrep(seq).strip())
            i += 1


# searchers for a keyword
# returns descirptor based on key word
def keyWordSearcher(course, initialDescription):
    descriptor = initialDescription
    if "Requirements" in course:
        if "Computer" in course:
            #descriptor = "Computer Science"
            descriptor = "CS"
        elif "Data" in course:
            #descriptor = "Data Science"
            descriptor = "DS"
        elif "Software" in course:
            #descriptor = "Software Enginner"
            descriptor = "SE"
        elif "Computing" in course:
            #descriptor = "Computing & Informatics"
            descriptor = "CI"
        elif "Information" in course:
            #descriptor = Information Systems"
            descriptor = "IS"
        elif "Science" in course:
            #descriptor = "Science"
            descriptor = "SCI"
        elif "Mathematics" in course:
            #descriptor = "Mathematics"
            descriptor = "MTH"
        elif "Arts & Humanities" in course:
            #descriptor = "Arts & Humanities"
            descriptor = "ArH"
        elif "University" in course:
            #descriptor = "University"
            descriptor = "Unv"
        else:
            descriptor = "None?"
    return descriptor
    
def parseDegreeRequiremnts(degreeName):
    
    if degreeName == "CS":
        course_catalog = requests.get("https://catalog.drexel.edu/undergraduate/collegeofcomputingandinformatics/computerscience/#requirementsbstext").text
        parsed_course_catalog = BeautifulSoup(course_catalog, 'html.parser')
        course_list = parsed_course_catalog.find_all('table', class_='sc_courselist')
    
        degree_frame = pd.DataFrame()
        degree_frame = pd.read_html(str(course_list))[0]
        degree_frame.columns = ['Courses', 'Label', 'Credits']
    elif degreeName == "SE":
        course_catalog = requests.get("https://catalog.drexel.edu/undergraduate/collegeofcomputingandinformatics/softwareengineering/#degreerequirementstext").text
        parsed_course_catalog = BeautifulSoup(course_catalog, 'html.parser')
        course_list = parsed_course_catalog.find_all('table', class_='sc_courselist')
    
        degree_frame = pd.DataFrame()
        degree_frame = pd.read_html(str(course_list))[0]
        degree_frame.columns = ['Courses', 'Label', 'Credits']
    elif degreeName == "DS":
        course_catalog = requests.get("https://catalog.drexel.edu/undergraduate/collegeofcomputingandinformatics/datascience/#degreerequirementstext").text
        parsed_course_catalog = BeautifulSoup(course_catalog, 'html.parser')
        course_list = parsed_course_catalog.find_all('table', class_='sc_courselist')
    
        degree_frame = pd.DataFrame()
        degree_frame = pd.read_html(str(course_list))[0]
        degree_frame.columns = ['Courses', 'Label', 'Credits']
    
    return degree_frame


          

def printList(list):
    for item in list:
        print(item)
"""
if __name__ == '__main__':
    ## modified poorly
    while True:
        try:
            course_catalog = requests.get("https://catalog.drexel.edu/undergraduate/collegeofcomputingandinformatics/computerscience/#requirementsbstext").text
            if course_catalog == "":
                print("Empty URL try again")
                continue
            break
        except:
            print("Invalid URL try again")
        
    parsed_course_catalog = BeautifulSoup(course_catalog, 'html.parser') 
    course_list = parsed_course_catalog.find_all('table', class_='sc_courselist')
    
    ## modification ends
    cs_degree_frame = parseDegreeRequiremnts("CS")

    #displayDF(cs_degree_frame)


    print("Degree Requirements: ")
   # printList(parseThroughClasses(cs_degree_frame))
    tempDf = parseThroughClasses(cs_degree_frame)
    #displayDF(tempDf)
    #displayDF(cs_degree_frame)
    displayDegree(tempDf, "Computer Science")

    #se_degree_frame = parseDegreeRequiremnts("DS")
    #tempDf = parseThroughClasses(se_degree_frame)
    #displayDegree(tempDf, "Data Science")


"""



    
  
        



    