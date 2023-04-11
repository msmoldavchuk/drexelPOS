import requests
from bs4 import BeautifulSoup
import pandas as pd
from course import Course as c
from sequence import Sequence as s, LinkedList, Node
from degree import Degree as d
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import random # test line
import csv 
from ast import literal_eval
import re
# DATA CHANGES
# MODIFY PHYS 101 SINCE DREXEL PREREQS ARE WRONG
# MODIFY CI 492 and 493 aviability they are wrong

# pip3 lxml


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
# lets go baby more globals
course_int_dictionary = {}
# i mean might as well make more globals
filtered_prerequiste_ditctionary = {}

keyword_descriptor = {
        "Computer" : "CS",
        "Data Science": "DS", 
        "Software": "SE", 
        "Computing": "CI", 
        "Information": "IS", 
        "Science": "SCI", 
        "Mathematics":"MTH",
        "Humanities": "HUM", 
        "University": "Unv", 
        "Statistics": "Stat",
        "Programing": "Prg"
    }

#creditsInWrongPlaceBoolean = False
LOC = ["Arts and Sciences","Bennett S. LeBow Coll. of Bus.","Center for Civic Engagement","Close Sch of Entrepreneurship","Col of Computing & Informatics","College of Engineering","Dornsife Sch of Public Health","Goodwin Coll of Prof Studies","Graduate College", "Miscellaneous","Nursing & Health Professions","Pennoni Honors College","Sch.of Biomed Engr,Sci & Hlth","School of Education","Thomas R. Kline School of Law"]

FRESHMAN = 0
SOPHMORE = 40
PREJUNIOR = 70.5
JUNIOR = 96.5
SENIOR = 130

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

    temp = False
    restrictionString = "None"
    for child in html_course:
        if temp:
            restrictionString = child
            break
        if child.text == "Restrictions:":
            temp = True
    # Create a course object w/ Course Id, Credits and UNFORMATED prereqstring
    # Adds course object to dictonatiy w/ the key value being the course id
    # i.e CS 172 maps to course object for CS 172 
    course_dictionary[cleanWIFormating(course_id.replace("\xa0", " "))] = c(cleanWIFormating(course_id.replace("\xa0", " ")), course_credits, prereqString, [False, False, False, False], restrictionString)
   
# This is a special method that processes elective requiremnts from a cs page
# It is a incomplete
def process_requiremnt_html():
    
    url = "https://catalog.drexel.edu/undergraduate/collegeofcomputingandinformatics/computerscience/#requirementsbstext"
    url = requests.get(url).text
    scrapper = BeautifulSoup(url, 'html.parser')
    scrapperScraped = scrapper.find_all('ul')
    #for sc in scrapperScraped:
   #     print(sc.text)
    return scrapperScraped[2].text

# scrapes a degree and gets a dataframe containing the requiremnts
def parseDegreeRequiremnts(degreename)->list:
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

    degreeReq = pd.read_html(str(course_list))
    degreeReqArray = []
    degree_frame = pd.DataFrame()
    
    for degree in degreeReq:
        degree_frame = degree
        degree_frame.columns = ['Courses', 'Label', 'Credits']
        degreeReqArray.append(degree_frame)

    return degreeReqArray

# A part of obtaining avalibility
# Gets Tables and returns as dataframes
def getTable(driver, intQuarter = 0):
    table = driver.find_element(By.ID, "sortableTable")
    intergrateAviability(pd.read_html(table.get_attribute('outerHTML'))[0], intQuarter)
    return pd.read_html(table.get_attribute('outerHTML'))[0]

# a part of obtaitining availiblity
# get's each webbage
def goThroughCollege(driver, textlink,tables, intQuarter = 0):
    try:
        driver.find_element(By.LINK_TEXT, textlink).click()
        tables.append(getTable(driver, intQuarter))
        driver.find_element(By.LINK_TEXT, "Colleges / Subjects").click()
        return tables
    except:
        print("error")
        return "error"

# get's all urls from the undergraduate course catalog
def getUrls() -> list:
    listofUrls = []
    html = requests.get("https://catalog.drexel.edu/coursedescriptions/quarter/undergrad/").text
    parsed_course_catalog = BeautifulSoup(html, 'html.parser')
    parsed_course_catalog = parsed_course_catalog.find_all('div', class_="qugcourses")
    #the two list
    for list_courses in parsed_course_catalog:
        #urls in each list
        urls = list_courses.find_all('a')
        for url in urls:
            print("https://catalog.drexel.edu" + url.get('href'))
            listofUrls.append("https://catalog.drexel.edu" + url.get('href'))
    return listofUrls

# processing algorithm for concentatrations
# gets a list of dataframes as a paramaeter
# returns a dataframe contaning a processed concentrartion
def getConcentration(dfList)->pd.DataFrame:
    concentrationDF = pd.DataFrame({'Concentration':[], "Name":[]})
    for df in dfList:
        coursesNotPrimary = df.loc[:,'Courses']
        courseDesc = df.loc[:,"Label"]
        credits = df.loc[:,'Credits']
        courses = []
        for course in coursesNotPrimary:
            courses.append(course.replace("\xa0", " "))

        coursesParsed = []
        creditsParsed = []
        descriptionsParsed = []
        flagParsed = [] # 0 = no problem, 1 = elective, 2 = choose, 3 = sequence, 4 = or

        seqString = ""

        descriptorRequired = filterDescription(courses[0])
        strlength = 12
        seqFlag = False

        for i in range(1, len(courses)):

            if seqFlag:
                if seqString == "" and (len(courses[i]) <= strlength and has_identifier(courses[i], "Digit")):
                    seqString = courses[i]
                elif (len(courses[i]) <= strlength and has_identifier(courses[i], "Digit")):
                    seqString += " | " + courses[i]
                else:
                    seqFlag = False
                    coursesParsed.append(seqString)
                    creditsParsed.append(credits[i])
                    descriptionsParsed.append(descriptorRequired)
                    flagParsed.append(2)
            elif len(courses[i]) <= strlength and has_identifier(courses[i], "Digit"):
                coursesParsed.append(courses[i])
                creditsParsed.append(credits[i])
                descriptionsParsed.append(descriptorRequired)
                
                if "*" in courseDesc[i]:
                    flagParsed.append(7)
                else:
                    flagParsed.append(0)

            elif has_identifier(courses[i], "Electives"):
                """
                if not checkForNoCredits(credits[i]):
                    coursesParsed.append("Elective")
                    creditsParsed.append(credits[i])
                    descriptionsParsed.append(descriptorRequired)
                    flagParsed.append(1)         
                """
                pass  
            elif has_identifier(courses[i], "Select"):
                """
                if not checkForNoCredits(credits[i]):
                    coursesParsed.append("Elective")
                    creditsParsed.append(credits[i])
                    descriptionsParsed.append(descriptorRequired)
                    flagParsed.append(1)   
                """   
                seqFlag = True     
            else:               
                dfPart = pd.DataFrame({"Sequence": coursesParsed, "Credits": creditsParsed, "Type": descriptionsParsed, "Flag": flagParsed, "Taken": False})
                coursesParsed = []
                creditsParsed = []
                descriptionsParsed = []
                flagParsed = []
                
                concentrationDF.loc[len(concentrationDF.index)] = [dfPart, descriptorRequired] 
                descriptorRequired = filterDescription(courses[i])


    
        dfPart = pd.DataFrame({"Sequence": coursesParsed, "Credits": creditsParsed, "Type": descriptionsParsed, "Flag": flagParsed, "Taken": False})
        concentrationDF.loc[len(concentrationDF.index)] = [dfPart, descriptorRequired] 
        
    return concentrationDF

# A means of filtering the description for the concentrartion
# it is sent a string and then returns the string containing everything before for "Concentration"
def filterDescription(string):
    if has_identifier(string, "Concentration"):
        string = string[:string.index("Concentration")-1]
    return string

    


#------------------------------------------METHODS TO CLEAN SCRAPPED DATA--------------------------------------

# Filters through scrapped degree data 
# Paramater is a list of dataframes formated with ("Courses", "Credits")
# returns a degree object
def parseThroughClasses(dfList)-> d: 

    # turn columns of data frame into arrays
    coursesNotPrimary = dfList[0].loc[:,'Courses']
    credits = dfList[0].loc[:,'Credits']
    courses = []


    for course in coursesNotPrimary:
        courses.append(course.replace("\xa0", " "))
        
    dfList.pop(0)

    #empty arrays to be filled during process and then turned into Dataframe
    coursesParsed = []
    creditsParsed = []
    descriptionsParsed = []
    flagParsed = [] # 0 = no problem, 1 = elective, 2 = mandatory


    electiveReqsDictonary = {}

    # support vars for looping
    seqFlag = False
    selectFlag = False
    choseFlag = False
    descriptorRequired = ""
    inc = 1
    myiter = iter(range(0, len(courses)))
    strlength = 12 #temp value

    # concentration vars
    concDF = pd.DataFrame()
    concBoolean = False
    concCredits = 0

    # use iter for sequence case
    for i in myiter:
        descriptorRequired = keyWordSearcher(courses[i], descriptorRequired) #step 1 check the type of course i.e cs or se

        if checkForNoCredits(credits[i]) and i >= 1:   #step 2 check if the credits exist if not then get previous
            credits[i] = credits[i-inc]
        #courses[i] = cleanBrackets(courses[i])

        if selectFlag == True:
            if ((len(courses[i]) <= strlength and has_identifier(courses[i], "Digit"))): #step 5 look for courses
                if flagParsed[-1] == 6:
                    ns = str(coursesParsed[len(coursesParsed)-1]) + " | " + str(courses[i])         #take previous parsed and add to the new line    
                    coursesParsed[len(coursesParsed)-1] = ns
                    descriptionsParsed[len(descriptionsParsed)-1] = descriptorRequired
                    flagParsed[len(flagParsed)-1] = 6
                elif flagParsed[-1] == 1:
                    coursesParsed[-1] = courses[1]
                    creditsParsed[-1] = credits[i]
                    flagParsed[-1] = 6
                    descriptionsParsed[-1] = descriptorRequired
                else:
                    coursesParsed.append(courses[i])
                    creditsParsed.append(credits[i])
                    flagParsed.append(6) # 6 = sel flag
                    descriptionsParsed.append(descriptorRequired)
            else:
                selectFlag = False

        if not seqFlag and not selectFlag and not choseFlag: # step 3 check if sequence mode
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
                if has_identifier(courses[i],"*"):
                    coursesParsed.append(courses[i][:len(courses[i])])
                    creditsParsed.append(credits[i])
                    descriptionsParsed.append(descriptorRequired)
                    flagParsed.append(2)
                else:
                    coursesParsed.append(courses[i])
                    creditsParsed.append(credits[i])
                    descriptionsParsed.append(descriptorRequired)
                    flagParsed.append(0)
            elif "concentration" in courses[i]:
                concBoolean = True
                concCredits = credits[i]
                concDF = getConcentration(dfList)
            elif "sequences:" in courses[i]: #step 7 check if a sequence is comming up
                seqFlag = True  # if yes change modes
            elif "select" in courses[i] or "Select" in courses[i]:
                listExpression = re.findall("[A-Z][A-Z][A-Z][A-Z],|[A-Z][A-Z][A-Z],|[A-Z][A-Z],|[A-Z][A-Z][A-Z][A-Z]\)|[A-Z][A-Z][A-Z]\)|[A-Z][A-Z]\)|[A-Z][A-Z][A-Z][A-Z]\.|[A-Z][A-Z][A-Z]\.|[A-Z][A-Z]\.", courses[i])
                # SPECIAL CASE where an elective functions as a select
                if listExpression:
                    for j in range(len(listExpression)):
                        listExpression[j] = listExpression[j][0:len(listExpression[j])-1]
                    electiveReqsDictonary[descriptorRequired] = listExpression
                    if flagParsed[-1] != 1:
                        coursesParsed.append("elective")
                        creditsParsed.append(credits[i])
                        descriptionsParsed.append(reverseKeyWordSearcher(descriptorRequired))
                        flagParsed.append(1)
                else:
                    selectFlag = True
            elif has_identifier(courses[i], "elective") or has_identifier(courses[i], "Elective"): #step 6 check if the course has elective in it
                    flagParsed.append(1) #elective flag
                    if(has_identifier(courses[i], "Free")): #free electives = end of program
                        coursesParsed.append("Elective")
                        creditsParsed.append(credits[i]) 
                        descriptionsParsed.append("Special") #special internal descriptor 

                        flagParsed.append(1)
                        coursesParsed.append("Total")
                        creditsParsed.append(credits[i+1]) 
                        descriptionsParsed.append("Special")

                    else: #not free elective then continue
                        if has_identifier(courses[i], "elective"):
                            specialString = courses[i][:courses[i].find("elective")-1]
                        else:
                            specialString = courses[i][:courses[i].find("Elective")-1]

                        coursesParsed.append("Elective") 
                        creditsParsed.append(credits[i])
                        descriptionsParsed.append(specialString)
        elif seqFlag == True: #step 4 sequence procedure activated 
            if ((len(courses[i]) <= strlength and has_identifier(courses[i], "Digit")) or has_identifier(courses[i], "&")): #step 5 look for courses
                if flagParsed[-1] == 3:
                    ns = str(coursesParsed[len(coursesParsed)-1]) + " ^ " + str(courses[i])         #take previous parsed and add to the new line    
                    coursesParsed[len(coursesParsed)-1] = ns
                    descriptionsParsed[len(descriptionsParsed)-1] = descriptorRequired
                    flagParsed[len(flagParsed)-1] = 3
                else:
                    coursesParsed.append(courses[i])
                    creditsParsed.append(credits[i])
                    flagParsed.append(3)
                    descriptionsParsed.append(descriptorRequired)
            elif courses[i][0:2].lower() == "or": #step 6 look for or keyword *different than prior
                #Sequence ors get their own line
                i += 1 #skip current line and go to next one
                inc = 2  # ancounts for skip in line                                                    
                ns = str(coursesParsed[len(coursesParsed)-1]) + " ^ " + str(courses[i])         #take previous parsed and add to the new line    
                coursesParsed[len(coursesParsed)-1] = ns
                descriptionsParsed[len(descriptionsParsed)-1] = descriptorRequired
                flagParsed[len(flagParsed)-1] = 3 # 3 = sequence flag                                        
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
                specialString = courses[i][:courses[i].find("elective")-1]
                coursesParsed.append("Elective")
                creditsParsed.append(credits[i])
                descriptionsParsed.append(specialString)
                flagParsed.append(1)
                seqFlag = False       # elective marks end of sequence         
            else:
                inc = 1
                seqFlag = False #emergancy way to end sequence
       

    # final step

    
    seqArray = []
    for course in coursesParsed:
        seqArray.append(s(course)) #convert filtered courses into array of sequence objects
    # concentrations
    #displayDF(concDF)

    if concBoolean:
        for i in range(len(concDF.index)):
            for j in range(len(concDF.loc[i, "Concentration"].loc[:,"Sequence"].index)):
                if checkForNoCredits(concDF.loc[i, "Concentration"].loc[j, "Credits"]):
                    concDF.loc[i, "Concentration"].loc[j, "Credits"] = course_dictionary[concDF.loc[i, "Concentration"].loc[j, "Sequence"]].getCredits()       
                concDF.loc[i, "Concentration"].loc[j, "Sequence"] = s(concDF.loc[i, "Concentration"].loc[j, "Sequence"])
        return d(seqArray, creditsParsed, descriptionsParsed, flagParsed, concDF, concCredits, requiredConcentration=True, requiredMinor=False)
        
    
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

def cleanBrackets(string)->str:
    while(has_identifier(string, "[") or has_identifier(string, "]")):
        x = string[string.index('['):string.index(']')+1]
        string = string.replace(x,"")    
    return string

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

    if "Requirements" in course:
        for keyword in keyword_descriptor.keys():
            if keyword in course:
                return keyword_descriptor[keyword]
        descriptor = "None?"
                
    return descriptor

def reverseKeyWordSearcher(descriptor):
    keyword_descriptor_reverse = reverseDict(keyword_descriptor)
    return keyword_descriptor_reverse[descriptor]

def reverseDict(dict:dict):
    dict2 = {}
    for i in range(len(dict)):
        dict2[list(dict.values())[i]] = list(dict.keys())[i]
    return dict2
#-----------------------------------------------------------------------------------------------------

# sent a course object
# is a void method but it recusrivly cycles if the course object has any prereqs
def prereqCycle(course: c): 
    tempArrayPrereqs = course.getPrereqArray() #gets an array of linked lsits representing pre reqs
    antiRecurrsionArray = []
    for prereqs in tempArrayPrereqs: #gets linked lists which represent 1 pre req sequence
        prereqsArray = prereqs.iterateThroughArray()
        for prereq in prereqsArray:
            if prereq != "":
                try:
                    course_dictionary[prereq.strip()]
                    appendToDictonaray(prereq)
                except KeyError:
                    # checks if it needs writing intensive added
                    try:
                        prereq += " [WI]"
                        course_dictionary[prereq.strip()]
                        appendToDictonaray(prereq)
                    except:
                        pass # class doesn't exist so its gonna be ignored

                prereqCourse = course_dictionary[prereq.strip()]
                if prereqCourse.getPrereqArray() != "":
                    #prereqCycle(prereqCourse)
                    antiRecurrsionArray.append(prereqCourse)
    recurssionIsTrash(antiRecurrsionArray)

# helper method for recursion in pre req cycle
def recurssionIsTrash(array):
    for a in array:
        prereqCycle(a)

# appends an item to the global course_int_dictinoary
# maps the key as a course object and adds 1 for each isntance of that object in the dictonary
def appendToDictonaray(item):
        try:
            # implement dictinaray
            course_int_dictionary[str(item).strip()] += 1  
        except KeyError:
            #print(item)
            try:
                course_int_dictionary.update({str(item).strip(): 1})
            except KeyError:
                print("Never seen this might as well put text? " + str(item))

# method that uses appendToDictonary and PrereqCycle
# sent a dataframe containing required courses and a columName depending on iof the colum is seqeuence or something else
def prereqDictionaryFill(df: pd.DataFrame, columName = "Sequence"):
    for i in range(len(df.index)):
        if columName == "Sequence":
            seqArray = df.loc[i,columName]
            for seq in seqArray.getSequence():
            # print("Sequence: " +str(seq))
                courseArray = seq.iterateThroughArray()
                for course in courseArray:
                    try:
                        if course == "Elective" or course == "Total":
                            pass
                        else:
                            appendToDictonaray(str(course).strip())
                            prereqCycle(course_dictionary[str(course).strip()])
                    except KeyError:
                        pass
        else:
            course = df.loc[i, columName]
            try:
                if course == "Elective" or course == "Total":
                    pass
                else:
                    appendToDictonaray(str(course).strip())
                    prereqCycle(course_dictionary[str(course).strip()])
            except KeyError:
                pass


# recives a data frame with a varying column name
# creates a new dataframe based on the first one
def filterPrereqDictionary(df: pd.DataFrame, columName = "Sequence"):
    filteredPrequistes = pd.DataFrame({'Courses':[], 'Value':[], 'Taken':[]})
    for i in range(len(df.index)):
        if columName == "Sequence":
            seqArray = df.loc[i,columName]
            for seq in seqArray.getSequence():
                courseArray = seq.iterateThroughArray()
                for course in courseArray:
                    try:
                        if course != "Elective":
                            filteredPrequistes.loc[len(filteredPrequistes.index)] = [str(course).strip() , course_int_dictionary[str(course).strip()], False]
                    except KeyError:
                        pass
        else:      
            try:
                filteredPrequistes.loc[len(filteredPrequistes.index)] = [str(df.loc[i, columName]).strip() , course_int_dictionary[str(df.loc[i, columName]).strip()], False]
            except:
                pass

    #filteredPrequistes.columns = ['Courses', 'Credits']
    return filteredPrequistes

# Paramater dataframe and quarter (0 to 3)
# void method
# Modifies course object by altering availbility array to True
def intergrateAviability(df: pd.DataFrame, quarter: int):
    
    for i in range(len(df.index)):
        try:
            courseName = str(df.loc[i,"Subject Code"]) + " " + str(df.loc[i, "Course No."])
            course_dictionary[courseName.replace("\xa0", " ")].setAviabilityTrue(quarter)
        except KeyError:
            try:
                courseName += " [WI]"
                course_dictionary[courseName.replace("\xa0", " ")].setAviabilityTrue(quarter)
            except KeyError:
                pass
    
#-----------------------------------------METHODS FOR DEBUGGING--------------------------------------------

# display data frame
def displayDF(df):
     with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(df)
        print("printed")          

# displays a list
def printList(list):
    for item in list:
        print(item)

# converts a csv into a dictonary of course objects
def convertCSVToCourseObject():
   #df = pd.read_csv("in.csv",converters={"Col3": literal_eval})
    
    df = pd.read_csv("courseObjects4.csv",converters={3:literal_eval})

    #df = pd.read_csv("courseObjects.csv") 
    df.columns = ['Courses', 'Credits', 'Prereqs', "Avail", "Enrollment"]
    for i in range(len(df.index)):
        if pd.notna(df.loc[i,"Prereqs"]):
            if pd.notna(df.loc[i, "Enrollment"]):
                course_dictionary[df.loc[i, "Courses"]] = c(df.loc[i, "Courses"], df.loc[i, "Credits"], df.loc[i, "Prereqs"], df.loc[i, "Avail"], df.loc[i, "Enrollment"])
            else:
                course_dictionary[df.loc[i, "Courses"]] = c(df.loc[i, "Courses"], df.loc[i, "Credits"], df.loc[i, "Prereqs"], df.loc[i, "Avail"], "")

        else:
            if pd.notna(df.loc[i, "Enrollment"]):
                course_dictionary[df.loc[i, "Courses"]] = c(df.loc[i, "Courses"], df.loc[i, "Credits"], "", df.loc[i, "Avail"], df.loc[i, "Enrollment"])
            else:
                course_dictionary[df.loc[i, "Courses"]] = c(df.loc[i, "Courses"], df.loc[i, "Credits"], "", df.loc[i, "Avail"], "")

# converts a course object into a csv
def convertCourseObjectToCSV():
    filename = 'courseObjects4.csv'
    try:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            for key in course_dictionary:
                courseObj = course_dictionary[key]
                if isinstance(courseObj.getPrereqString(), type(None)) or courseObj.getPrereqString() == "":
                    writer.writerow([cleanWIFormating(courseObj.getCourseName()), courseObj.getCredits(), "", courseObj.getAvial(), courseObj.getRestrctionString()])
                else:
                    writer.writerow([cleanWIFormating(courseObj.getCourseName()), courseObj.getCredits(), courseObj.getPrereqString(), courseObj.getAvial(), courseObj.getRestrctionString()])

    except BaseException as e:
        print('BaseException:', filename)

# cleans up inconsitancy in [wi] formating
def cleanWIFormating(string)->str:
        # CS 26   [WI]
        while(has_identifier(string, "  ")):
            string = string.replace("  "," ")    
        return string

# scrapes the course catalog
def scrapeCourseCatalog():
    urls = getUrls()
    for url in urls:
        print(url)
        try:
            #course_catalog = requests.get(input("Enter the course catalog: ")).text
            course_catalog = requests.get(url).text #gets website for cs
            if course_catalog == "":
                print("Empty URL try again")
                continue
          
        except:
            print("Invalid URL try again")
                #html things
        parsed_course_catalog = BeautifulSoup(course_catalog, 'html.parser')
        course_list = parsed_course_catalog.find_all('div', class_='courseblock')
            # processes each entry
        for course in course_list:
            #print(course)
            process_course_html(course)

# scrapes term master schedule
def scrapeTermMaster():
    listofQuaters = ["Fall Quarter 22-23","Winter Quarter 22-23","Spring Quarter 22-23","Summer Quarter 22-23"]
    driver = webdriver.Edge()
    driver.get("https://termmasterschedule.drexel.edu/webtms_du/")
    #print(goingthroughacollege(driver))
    intQuarter = 0
    tables = []
    counterQ = 0
    driver.get("https://termmasterschedule.drexel.edu/webtms_du/")
    #driver.find_element(By.LINK_TEXT, Q).click()
    file = open("C:\\Users\\micha\\ci102\\pos\\tempStorage", "r")
    for line in file:
        if("Fall Quarter 22-23" == str(line).replace("\n", "")):
            intQuarter = 0
            driver.get("https://termmasterschedule.drexel.edu/webtms_du/")
            driver.find_element(By.LINK_TEXT, "Fall Quarter 22-23").click()
            time.sleep(.1)
            counterQ = 0
            continue
        if("Winter Quarter 22-23" == str(line).replace("\n", "")):
            intQuarter = 1
            driver.get("https://termmasterschedule.drexel.edu/webtms_du/")
            driver.find_element(By.LINK_TEXT, "Winter Quarter 22-23").click()
            print("Winter Quarter 22-23")
            time.sleep(.1)
            counterQ = 0
            continue
        if("Spring Quarter 22-23" == str(line).replace("\n", "")):
            intQuarter = 2
            driver.get("https://termmasterschedule.drexel.edu/webtms_du/")
            driver.find_element(By.LINK_TEXT, "Spring Quarter 22-23").click()
            print("Spring Quarter 22-23")
            time.sleep(.1)
            counterQ = 0
            continue
        if("Summer Quarter 22-23" == str(line).replace("\n", "")):
            intQuarter = 3
            driver.get("https://termmasterschedule.drexel.edu/webtms_du/")
            driver.find_element(By.LINK_TEXT, "Summer Quarter 22-23").click()
            print("Summer Quarter 22-23")
            time.sleep(.1)
            counterQ = 0
            continue
        print(line.encode("utf-8"))
        try:
            if(goThroughCollege(driver, str(line).replace("\n", ""), tables, intQuarter) == "error"):
                raise Exception("error")
        except:
            try:
                print(line.encode("utf-8"))
                driver.find_element(By.LINK_TEXT, LOC[counterQ]).click()
                counterQ += 1
                goThroughCollege(driver, str(line).replace("\n", ""), tables, intQuarter)
            except:
                counterQ += 1
                print(line.encode("utf-8"))
                goThroughCollege(driver, str(line).replace("\n", ""), tables, intQuarter)

# paramater are a boolean representing ssCoop and term (0-3)
# returns if one would have coop based on that info
def coopBooleanFinder(springSummerCoop, term):
    coopBoolean = False
    if springSummerCoop:
        if term == 2 or term == 3:
            #print("COOP") # coop
            coopBoolean = True
        else:
            coopBoolean = False
    else:
        if term == 0 or term == 1:
        # print("COOP") # coop
            coopBoolean = True
        else:
            coopBoolean = False
    return coopBoolean

# paramater is a dataframe of courses (string form)
# returns an array of availibity in each of those terms
# UNUSED IN CALCULATIONS
def calculateQuarterlyAvail(df):
    fallCounter = 0
    winterCounter = 0
    springCounter = 0
    summerCounter = 0
    for i in range(len(df.index)):
        try:
            if course_dictionary[df.loc[i,"Courses"]].getFallAvail():
                fallCounter += 1

            if course_dictionary[df.loc[i,"Courses"]].getWinterAvail():
                winterCounter += 1

            if course_dictionary[df.loc[i,"Courses"]].getSpringAvail():
                springCounter += 1

            if course_dictionary[df.loc[i,"Courses"]].getSummerAvail():
                summerCounter += 1
        except KeyError:
            pass
        
    return [fallCounter, winterCounter, springCounter, summerCounter]

# paramater is a dataframe of courses (string form)
# returns an array of availibity if a course is only offered once a year
# UNUSED IN CALCULATIONS
def calculateQuarterlySingularAvail(df):
    fallCounter = 0
    winterCounter = 0
    springCounter = 0
    summerCounter = 0
    for i in range(len(df.index)):
        try:
            if course_dictionary[df.loc[i,"Courses"]].getFallAvail() and not (course_dictionary[df.loc[i,"Courses"]].getWinterAvail() or course_dictionary[df.loc[i,"Courses"]].getSpringAvail() or course_dictionary[df.loc[i,"Courses"]].getSummerAvail()):
                fallCounter += 1

            if course_dictionary[df.loc[i,"Courses"]].getWinterAvail() and not (course_dictionary[df.loc[i,"Courses"]].getFallAvail() or course_dictionary[df.loc[i,"Courses"]].getSpringAvail() or course_dictionary[df.loc[i,"Courses"]].getSummerAvail()):
                winterCounter += 1

            if course_dictionary[df.loc[i,"Courses"]].getSpringAvail() and not (course_dictionary[df.loc[i,"Courses"]].getWinterAvail() or course_dictionary[df.loc[i,"Courses"]].getFallAvail() or course_dictionary[df.loc[i,"Courses"]].getSummerAvail()):
                springCounter += 1

            if course_dictionary[df.loc[i,"Courses"]].getSummerAvail() and not (course_dictionary[df.loc[i,"Courses"]].getWinterAvail() or course_dictionary[df.loc[i,"Courses"]].getSpringAvail() or course_dictionary[df.loc[i,"Courses"]].getFallAvail()):
                summerCounter += 1
        except KeyError:
            pass
        
    return [fallCounter, winterCounter, springCounter, summerCounter]

# method for predetierimend courses
# paramaeter is a course and a dataframe
# changes the course to taken and returns the dataframe altough since it is a ref type that is not needed
def assignPredeterminedCourse(course: str, df: pd.DataFrame)->pd.DataFrame:
    for i in range(len(df.index)):
        if df.loc[i, "Courses"] == course:
            df.loc[i, "Taken"] = True
            return df
    # if it makes it here the course is not in the dataframe so add it

    df.loc[len(df.index)] = [str(course).strip(), 0, True]
    return df

# prints a plan of study 
# paramater is plan of study
def printPlanOfStudy(posArray):
    print("Plan of Study")
    counter = 0
    firstYear = True
    year = 2022
    for quarter in posArray:
        if counter == 0:
            print(str(year) + str(15))
        elif counter == 1:
            print(str(year) + str(25))
        elif counter == 2:
            print(str(year) + str(35))
        elif counter == 3 and not firstYear:
            print(str(year) + str(45))
        else:
            firstYear = False
            counter *= 0
            year+=1
            print(str(year) + str(15))
        miniCounter = 1
        for classes in quarter:
            print("\t"+str(miniCounter)+"." + classes)  
            miniCounter += 1     
        counter+= 1

# converts plan of study to a dictonary
# paramater is plan of study
def convertToDictionary(posArray):
    counter = 0
    firstYear = True
    year = 2022
    dictonary = {}
    for quarter in posArray:
        if counter == 0:
            dictonary.update({(str(year) + str(15)):  quarter})
        elif counter == 1:
            dictonary.update({(str(year) + str(25)):  quarter})
        elif counter == 2:
            dictonary.update({(str(year) + str(35)):  quarter})
        elif counter == 3 and not firstYear:
            dictonary.update({(str(year) + str(45)):  quarter})
        else:
            firstYear = False
            counter *= 0
            year+=1
            dictonary.update({(str(year) + str(15)):  quarter})       
        counter+= 1
    return dictonary
    
# gets a special dataframe
# makes a copy to avoid refrence issues
# paramaters are a dataframe and an array of assinged courses
# sets all courses in the array to false in the dataframe
def filterOnCurrent(df: pd.DataFrame, coursesAssigned):
    
    df2 = df.copy()
    for course in coursesAssigned:
        for i in range(len(df2.index)):
            if df.loc[i, "Courses"].strip() == course.strip():  
                df2.loc[i, "Taken"] = False
                
    return df2

# paramaters are dataframe and number of each type of quarter in array form
# returns a special data frame(codded copy)
def availCalculator(df: pd.DataFrame, numberOfArray, quarter):
    # quarter 0 = fall, 1 = winter, 2 = spring, 3 = summer
    df2 = df.copy(True)
    fMulti = 0
    wMulti = 0
    sMulti = 0
    suMulti = 0
    limiter = 0
    for i in range(len(df2.index)):
        try:
            # 3.5 is a magic number
            if course_dictionary[df2.loc[i, "Courses"]].getFallAvail():
                fMulti = numberOfArray[0] / df.loc[i, "Value"] / 3.5
            if course_dictionary[df2.loc[i, "Courses"]].getWinterAvail():
                wMulti = numberOfArray[1] / df.loc[i, "Value"] / 3.5
            if course_dictionary[df2.loc[i, "Courses"]].getSpringAvail():
                sMulti = numberOfArray[2] / df.loc[i, "Value"] / 3.5
            if course_dictionary[df2.loc[i, "Courses"]].getSummerAvail():
                suMulti = numberOfArray[3] / df.loc[i, "Value"] / 3.5
            """
            avialQuarters = course_dictionary[df2.loc[i, "Courses"]].getAvial()
            for i in range(len(avialQuarters)):
                if avialQuarters[i] == True and i == quarter:
                    limiter += 10
                elif avialQuarters[i] == True and i != quarter:
                    limiter -= 2
                else:
                    limiter += .5
            """
            if course_dictionary[df2.loc[i, "Courses"]].checkIfSequence():
                #print("flag")
                df2.loc[i, "Value"] = 100
            elif (fMulti + wMulti + sMulti + suMulti) + limiter > df.loc[i, "Value"]:
                df2.loc[i, "Value"] = .00000000001
                
                """
                print("Oof")
                print(df.loc[i,"Courses"])
                print("Val:"+str(df2.loc[i,"Value"]))
                print(str(fMulti))
                print(str(wMulti))
                print(str(sMulti))
                print(str(suMulti))
                """
            
            else:
                df2.loc[i, "Value"] = df2.loc[i, "Value"] - fMulti - wMulti - sMulti - suMulti + limiter
                """
                print("Doof")
                print(df.loc[i,"Courses"])
                print("Val:"+str(df2.loc[i,"Value"]))
                print(str(fMulti))
                print(str(wMulti))
                print(str(sMulti))
                print(str(suMulti))
                """
        except:
            pass
    #displayDF(df2)
    return df2

# gets credits as a paramter and returns a number signifiging the classifcation of a student
# higher the number = higher classification
def getClassification(credits):
    if credits >= SENIOR:
        return 5
    elif credits >= JUNIOR:
        return 4
    elif credits >= PREJUNIOR:
        return 3
    elif credits >= SOPHMORE:
        return 2
    else:
        return 1
    
# Paramters
# Dataframe containing "Courses" "Value" "Taken"
# Degree object
# quarter (0 to 3) represening a quarter as an index for arrays
# arrayOfBooleans array containing [firstYearBoolean, coopYearBoolean, finalYearBoolean]
# numberOfArray array representing the number of each type of term remaining w/ fall being [0] to summer being [3]
# classifcation int (0 to 4) representing freshman to senior
# credit goal int of number credits one wishes to take
# Returns
#An Array Containing:
# [0] An array of courses to be taken that term
# [1] theFileteredDataFrame with modifciations to courses taken
# [2] the DegreeObject
# [3] the number of credits taking  
def createPlanForTerm(filteredDataFrame, degreeReq: d, quarter, arrayOfBooleans, numberOfArray, classification, creditGoal)->list:
    #arrayOfBooleans = [firstYear, coopYear, finalYear] (note)

    credits = 0.0
    course = "First Class"
    prevCourse = "First Class"
    addedThisTerm = []
    arrayForTerm = []

    numberOfTermsThisYear = 4
    if arrayOfBooleans[0] == True:
        numberOfTermsThisYear = 3
    elif arrayOfBooleans[1] == True:
        numberOfTermsThisYear = 2
    elif arrayOfBooleans[2] == True:
        numberOfTermsThisYear = 3
    valueDf = availCalculator(filteredDataFrame, numberOfArray, quarter)
    #valueDf = filteredDataFrame
    
    while(creditGoal >= credits):
        max = 0
        pos = 1
        interalValue = 0
            # for pre req checking
        for j in range(len(filteredDataFrame.index)):
            try:
                if course_dictionary[filteredDataFrame.loc[j, "Courses"]].getMustAddBoolean():
                    course = filteredDataFrame.loc[j, "Courses"]
                    pos = j
                    course_dictionary[filteredDataFrame.loc[j, "Courses"]].setMustAddBoolean(False)
                elif not filteredDataFrame.loc[j, "Taken"]:
                    if not degreeReq.checkIfTaken(filteredDataFrame.loc[j, "Courses"]):
                        tempMax = valueDf.loc[j, "Value"] # uses value array w/ avail calcs
                        if tempMax > max: 
                            #print("!" + filteredDataFrame.loc[j , "Courses"])
                        
                            if course_dictionary[filteredDataFrame.loc[j, "Courses"]].getAvial()[quarter]:
                                if course_dictionary[filteredDataFrame.loc[j, "Courses"]].processCourseRequirments(classification):
                                    if  course_dictionary[filteredDataFrame.loc[j, "Courses"]].havePreqs(filterOnCurrent(filteredDataFrame, addedThisTerm)): #modify dataframe to make sure it address courses in the term
                                        #print("!!!" + filteredDataFrame.loc[j , "Courses"])
                                        if course_dictionary[filteredDataFrame.loc[j, "Courses"]].checkSequenceLength() < numberOfTermsThisYear:
                                            course = filteredDataFrame.loc[j, "Courses"]
                                            pos = j
                                            max = tempMax     
                                            interalValue = valueDf.loc[j,"Value"]                 
            except:
                pass

        
        if prevCourse != course:
            if interalValue == .00000000001 and (creditGoal - 4) <= credits: # for assinging undefined elective
                elective = degreeReq.pickElectiveRandom()
                if elective[0] == "No Class":
                    break
                else:
                    arrayForTerm.append(elective[0])
                    credits += float(elective[1])
                    prevCourse = elective[0]
                    addedThisTerm.append(elective[0])
            else:
                arrayForTerm.append(course)
                filteredDataFrame.loc[pos, "Taken"] = True
                credits += float(course_dictionary[course].getCredits())
                degreeReq.checkCompletion(filteredDataFrame)
                prevCourse = course
                addedThisTerm.append(course)
        else:
            if degreeReq.getFreeElectiveMode():
                while credits <= creditGoal:
                    elective = degreeReq.freeElectivesRandom()
                    if elective[0] == "No Class":
                        break
                    else:
                        arrayForTerm.append(elective[0])
                        credits += float(elective[1])
                        prevCourse = elective[0]
                        addedThisTerm.append(elective[0])
            
            for previousCourse in addedThisTerm:
                try:
                    course_dictionary[previousCourse].adjustSequencePriority()
                except:
                    pass
            return [arrayForTerm, filteredDataFrame, degreeReq, credits]
    for previousCourse in addedThisTerm:
        try:
            course_dictionary[previousCourse].adjustSequencePriority()
        except:
            pass
    return [arrayForTerm, filteredDataFrame, degreeReq, credits]

# hard codes in sequence courses since this data is not scrapable
def correctSequences():
    course_dictionary["CI 102"].createSequence(course_dictionary["CI 103"])

    course_dictionary["CI 491 [WI]"].createSequence(course_dictionary["CI 492 [WI]"])
    course_dictionary["CI 492 [WI]"].createSequence(course_dictionary["CI 493 [WI]"])

# method to check if one takes coop 101
# recives the number of coops they plan on, their coop type, the year and the term
def takeCOOP101Checker(coopNumber, springSummerCoop, year, term): 
    if coopNumber == 3 and springSummerCoop and year == 1 and term == 2:
        return True
    elif coopNumber == 1 and springSummerCoop and year == 2 and term == 2:
        return True
    elif coopNumber == 3 and not springSummerCoop and year == 1 and term == 1:
        return True
    elif coopNumber == 1 and not springSummerCoop and year == 2 and term == 1:
        return True
    else:
        return False

# checks if it is possible to take all the classes in a list of courses if not possible it will add them
def checkIfPossible(degreeReq, filteredDataFrame):
    internalDf = pd.DataFrame({"Courses": filteredDataFrame.loc[:,"Courses"], "Value": filteredDataFrame.loc[:,"Value"], "Taken": True})
    for i in range(len(internalDf.index)):
        try:
            if not course_dictionary[internalDf.loc[i,"Courses"].strip()].havePreqs(internalDf):
                #print(""+internalDf.loc[i,"Courses"])       
                overrider = 0
                while True:
                    try:
                        course = course_dictionary[internalDf.loc[i, "Courses"]].findMissingPrereq(internalDf, overrider)
                        degreeReq.takeFreeElectives(course_dictionary[course].getCredits()) # see if course exists
                        filteredDataFrame.loc[len(filteredDataFrame.index)] = [course, 0, False]        
                        break
                    except:
                        overrider += 1
                return False
        except:
            pass
    return True

# displays all courses with no availiblity data w/in the concentration
def displayPhantomConcentrations(degreeReq):
    concDf = degreeReq.getConcentrationsTesting()
    #displayDF(concDf)
    for i in range(len(concDf.index)):
        miniConcDf = concDf.loc[i,"Concentration"]
        for j in range(len(miniConcDf.index)):
            try:
                course = course_dictionary[str(miniConcDf.loc[j,"Sequence"])]
                courseAvail = course.getAvial()
                tempBool = False
                for avail in courseAvail:
                    if avail:
                        tempBool = True
                if tempBool == False:
                    print(str(course) + " Phantom")
            except:
                pass

#Paramaters
# degree object
# dataframe of courses
# number of quarters one plans on having
# coop type
# how many credits they want per term
# how many coops
#Returns
#Plan of study array
def createPlan(degreeReq, filteredDataFrame, NUMBEROFQUARTERS = 18, SPRINGSUMMERCOOP =  True, CREDITGOAL = 15, COOPNUMBER = 3):
    if degreeReq.getDegreeCollege() == "CCI":
        #numberOfQuarters = 18
        #springSummerCoop = False
        #coopNumber = 3
        numTermsPremade = 1
        #creditMin = 15
        #creditMax = 17

        numberOfFalls = 5
        numberOfWinters = 5
        numberOfSprings = 5
        numberOfSummers = 5
        
        
        if SPRINGSUMMERCOOP:
            numberOfSprings = 2
            numberOfSummers = 0
        else:
            numberOfFalls = 2
            numberOfWinters = 2
            numberOfSummers = 3

        posArray = [] #array that contains the plan of study
        for i in range(NUMBEROFQUARTERS):
            posArray.append([])
        numberOfArray = [numberOfFalls, numberOfWinters, numberOfSprings, numberOfSummers]
        coopBoolean = False
        firstYear = True
        coopYear = False
        finalYear = False
      
        # templines
        numTermsPremade = 1
        #predetiermendCourses2 = ["MATH 201", "ENGL 102", "CI 102", "PHYS 101", "CIVC 101", "CS 172", "CS 171"]
        #predetiermendCourses3 = ["MATH 122", "ENGL 103", "CI 103", "CS 265","SE 181","CS 270", "UNIV CI101", "COOP 101"]
        # -------- pre decided terms -----------------
        firstTermPremade = True
        predetiermendCourses = ["CS 164", "PSY 101", "MATH 121", "ENGL 101", "CI 101"]
        #predetiermendCourses = ["INFO 101", "PSY 101", "MATH 121", "ENGL 101", "CI 101"]

        predetiermendCourseArray = [predetiermendCourses]

        credits = 0.0
        for i in range(numTermsPremade):
            if i == 0 and firstTermPremade:
                posArray[i].append("UNIV CI101")
                credits += 1

            for course in predetiermendCourseArray[i]:
                try:
                    posArray[i].append(course)
                    filteredDataFrame = assignPredeterminedCourse(course, filteredDataFrame)
                    credits += course_dictionary[course].getCredits()
                except:
                    #posArray[i].append(course)
                    #filteredDataFrame = assignPredeterminedCourse(course, filteredDataFrame)
                    credits += 1
            degreeReq.checkCompletion(filteredDataFrame)


        for i in range(numTermsPremade, NUMBEROFQUARTERS+1):
            year = 1
            totalQuarterAvail = calculateQuarterlyAvail(filteredDataFrame)
            #totalQuarterSingularAvail = calculateQuarterlySingularAvail(filteredDataFrame)
            term = i
            classification = getClassification(credits)
            #for QuarterAvail in totalQuarterAvail:
            #   print("A "+str(QuarterAvail))
            #   print("S "+str(totalQuarterSingularAvail))
            if term > 3:
                firstYear = False
                while term > 3:
                    term -= 4
                    year += 1

                if COOPNUMBER == 1 and year == 3:
                    coopYear = True
                    coopBoolean = coopBooleanFinder(SPRINGSUMMERCOOP, term)
                elif COOPNUMBER == 3 and (year == 2 or year == 3 or year == 4):
                    coopYear = True
                    coopBoolean = coopBooleanFinder(SPRINGSUMMERCOOP, term)
                else:
                    coopYear = False
                    coopBoolean = False
                    if COOPNUMBER == 1 and year == 4:
                        finalYear = True
                    elif COOPNUMBER == 3 and year == 5:
                        finalYear = True

            if not firstYear:
                i -= 1

            arrayOfBooleans = [firstYear, coopYear, finalYear]
            if term == 0:
                #print("Fall") # fall
                if coopBoolean:
                 #   print("\tCO-OP")
                    posArray[i].append("COOP 201")
                else:
                    numberOfArray[term] -= 1
                    outputArray = createPlanForTerm(filteredDataFrame, degreeReq, 0, arrayOfBooleans, numberOfArray, classification, CREDITGOAL)
                    posArray[i] = outputArray[0]
                    filteredDataFrame = outputArray[1]
                    degreeReq = outputArray[2] 
                    credits += outputArray[3]
                
            elif term == 1:

                #print("Winter") # winter
                if coopBoolean:
                 #   print("\tCO-OP")
                    posArray[i].append("COOP 201")
                else:
                    numberOfArray[term] -= 1
                    outputArray = createPlanForTerm(filteredDataFrame, degreeReq, 1, arrayOfBooleans, numberOfArray, classification, CREDITGOAL)
                    posArray[i] = outputArray[0]
                    filteredDataFrame = outputArray[1]
                    degreeReq = outputArray[2]
                    credits += outputArray[3]

                    if takeCOOP101Checker(COOPNUMBER, SPRINGSUMMERCOOP, year, term):
                        posArray[i].append("COOP 101")
                        filteredDataFrame = assignPredeterminedCourse("COOP 101", filteredDataFrame)
                        degreeReq.checkCompletion(filteredDataFrame)

            elif term == 2:
                #print("Spring") # spring

                if coopBoolean:
                 #   print("\tCO-OP")
                    posArray[i].append("COOP 201")
                else:
                    numberOfArray[term] -= 1
                    outputArray = createPlanForTerm(filteredDataFrame, degreeReq, 2, arrayOfBooleans, numberOfArray, classification, CREDITGOAL)
                    posArray[i] = outputArray[0]
                    filteredDataFrame = outputArray[1]
                    degreeReq = outputArray[2]
                    credits += outputArray[3]

                    
                    if takeCOOP101Checker(COOPNUMBER, SPRINGSUMMERCOOP, year, term):
                        posArray[i].append("COOP 101")
                        filteredDataFrame = assignPredeterminedCourse("COOP 101", filteredDataFrame)
                        degreeReq.checkCompletion(filteredDataFrame)
                    # 
                    if firstYear:
                        posArray[i].append("UNIV CI101")
                        filteredDataFrame = assignPredeterminedCourse("UNIV CI101", filteredDataFrame)
                        degreeReq.checkCompletion(filteredDataFrame)


            elif term == 3 and not firstYear:
                #print("Summer") # summer

                if coopBoolean:
                 #   print("\tCO-OP")
                    posArray[i].append("COOP 201")
                else:
                    numberOfArray[term] -= 1
                    outputArray = createPlanForTerm(filteredDataFrame, degreeReq, 3, arrayOfBooleans, numberOfArray, classification, CREDITGOAL)
                    posArray[i] = outputArray[0]
                    filteredDataFrame = outputArray[1]
                    degreeReq = outputArray[2]
                    credits += outputArray[3]

            print("_____________________________________________________________")
    return posArray

# Name of degree
# College it is in
# Type for Science Sequence
# Array of Concentrations format:
#    [ ["Name", [Course 1, Course2]], [Conecentration]]
#Returns the degree object
# TEMP CHANGE SE
def getCustomDegree(NAME = "SE", COLLEGE = "CCI", SEQUENCES = ["CHEM"], CONCENTRATIONARRAY =[["Algorithms and Theory", ["CS 457", "CS 300", "MATH 305"]], ["Artificial Intelligence and Machine Learning",["CS 380", "CS 383", "DSCI 351"]]]):
    degreeReq = d()
    degreeReq.convertCSVToDegree(NAME)
    degreeReq.setDegreeName(NAME)
    degreeReq.setDegreeCollege(COLLEGE)
    degreeReq.userChooseCourse(SEQUENCES, course_dictionary)
    #prereqDictionaryFill(degreeReq.getDegree())
    #concentration lines
    
    for concentration in CONCENTRATIONARRAY:
        degreeReq.selectConcentration(concentration[0], concentration[1])
    
    #prereqDictionaryFill(concDf)
    #prereqDictionaryFill(concDf2)
    return degreeReq

# testing method
def testPlanOfStudy(posArray, filteredDataFrame, degreeReq:d):
    printPlanOfStudy(posArray)
    displayDF(filteredDataFrame)
    counter = 0
    for i in range(len(filteredDataFrame.index)):
        if not filteredDataFrame.loc[i,"Taken"]:
            print(filteredDataFrame.loc[i, "Courses"])
            counter += 1
    print("Failed: " + str(counter))
    
    print(degreeReq)
    #degreeReq.displayDFMain()
    #displayDF(degreeReq.getElectives())
    
#paramters
# Name of degree
# College it is in
# Type for Science Sequence
# Array of Concentrations format:
#    [ ["Name", [Course 1, Course2]], [Conecentration]]
# dataframe of courses
# number of quarters one plans on having
# coop type
# how many credits they want per term
# how many coops
# TEMP CHANGE SE
def getPlanOfStudy(NAME = "SE", COLLEGE = "CCI",  SEQUENCES = ["CHEM"], CONCENTRATIONARRAY =[["Algorithms and Theory", ["CS 457", "CS 300", "MATH 305"]], ["Artificial Intelligence and Machine Learning",["CS 380", "CS 383", "DSCI 351"]]], NUMBEROFQUARTERS = 18, SPRINGSUMMERCOOP =  True, CREDITGOAL = 15, COOPNUMBER = 3):
    # -------SCRAPING----------
    """
    scrapeCourseCatalog()
    scrapeTermMaster()
    convertCourseObjectToCSV()
    """
    #-----Not Scraping-----
    convertCSVToCourseObject()
    correctSequences()
    #-----SET UP DEGREE--------------------
    degreeReq = getCustomDegree(NAME, COLLEGE, SEQUENCES, CONCENTRATIONARRAY)
    
    prereqDictionaryFill(degreeReq.getFullDegree())
    tempDf = filterPrereqDictionary(degreeReq.getFullDegree())
    checkIfMissing = False
    while(not checkIfMissing):
        checkIfMissing = checkIfPossible(degreeReq, tempDf)   
    course_int_dictionary.clear()

    prereqDictionaryFill(tempDf, "Courses")
    filteredDataFrame = filterPrereqDictionary(tempDf, "Courses")
    #----Get Plan of Study-------   
    posArray = createPlan(degreeReq, filteredDataFrame,  NUMBEROFQUARTERS, SPRINGSUMMERCOOP, CREDITGOAL, COOPNUMBER)
    #------Display Play of Study
    testPlanOfStudy(posArray, filteredDataFrame, degreeReq)
    return convertToDictionary(posArray)
   
#--------------------------------------String Process-------------------------
def electiveProcessing(unProcessedString: str):
    print(unProcessedString)
    if "electives" in unProcessedString:
        postColonString = unProcessedString[unProcessedString.index("electives")+10:] 
        if ":" in postColonString:
            #print(postColonString)
            postPreColonString = postColonString[:postColonString.index("electives")]  
            #print(postPreColonString)           
            electiveSlice = unProcessedString[:postPreColonString.rindex(" ")]
            singularString(electiveSlice) #method call
            remainderString = unProcessedString[:postPreColonString.rindex(" ")]            
            return remainderString
    
def singularString(unprocessedString):
    print(unprocessedString)

def scrapingDegree(NAME):
    convertCSVToCourseObject()
    list_degree_frame = parseDegreeRequiremnts(NAME)
    degreeReq = parseThroughClasses(list_degree_frame)
    return degreeReq

#------------------------------- EVERYTHING BELLOW IS "Main"----------------------------------------------
if __name__ == "__main__":
    #electiveProcessing(process_requiremnt_html())
    

    #convertCSVToCourseObject()
    #list_degree_frame = parseDegreeRequiremnts("CS")
    #degreeReq = parseThroughClasses(list_degree_frame)
    

    
    #degreeReq.convertDegreeToCSV("CS")
    #print(degreeReq)
    getPlanOfStudy(NAME = "CS", SEQUENCES=["CHEM"],SPRINGSUMMERCOOP=True, CONCENTRATIONARRAY=[])

    """
    convertCSVToCourseObject()
    correctSequences()
    #-----SET UP DEGREE--------------------
    degreeReq = getCustomDegree("SE", "CCI", "CHEM", CONCENTRATIONARRAY = [])
    print(degreeReq)
    """