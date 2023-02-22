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

#creditsInWrongPlaceBoolean = False
LOC = ["Arts and Sciences","Bennett S. LeBow Coll. of Bus.","Center for Civic Engagement","Close Sch of Entrepreneurship","Col of Computing & Informatics","College of Engineering","Dornsife Sch of Public Health","Goodwin Coll of Prof Studies","Graduate College", "Miscellaneous","Nursing & Health Professions","Pennoni Honors College","Sch.of Biomed Engr,Sci & Hlth","School of Education","Thomas R. Kline School of Law"]



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

    course_dictionary[course_id.replace("\xa0", " ")] = c(course_id.replace("\xa0", " "), course_credits, prereqString)
   


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
def getTable(driver, intQuarter = 0):
    table = driver.find_element(By.ID, "sortableTable")
    intergrateAviability(pd.read_html(table.get_attribute('outerHTML'))[0], intQuarter)
    return pd.read_html(table.get_attribute('outerHTML'))[0]

def goThroughCollege(driver, textlink,tables, intQuarter = 0):
    try:
        driver.find_element(By.LINK_TEXT, textlink).click()
        tables.append(getTable(driver, intQuarter))
        driver.find_element(By.LINK_TEXT, "Colleges / Subjects").click()
        return tables
    except:
        print("error")
        return "error"

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

def getConcentration(dfList)->pd.DataFrame:
    concentrationDF = pd.DataFrame({'Concentration':[], "Name":[]})
    for df in dfList:
        coursesNotPrimary = df.loc[:,'Courses']
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
                dfPart = pd.DataFrame({"Sequence": coursesParsed, "Credits": creditsParsed, "Type": descriptionsParsed, "Flag": flagParsed})
                coursesParsed = []
                creditsParsed = []
                descriptionsParsed = []
                flagParsed = []
                
                concentrationDF.loc[len(concentrationDF.index)] = [dfPart, descriptorRequired] 
                descriptorRequired = filterDescription(courses[i])


    
        dfPart = pd.DataFrame({"Sequence": coursesParsed, "Credits": creditsParsed, "Type": descriptionsParsed, "Flag": flagParsed})
        concentrationDF.loc[len(concentrationDF.index)] = [dfPart, descriptorRequired] 
        
    return concentrationDF


def filterDescription(string):
    if has_identifier(string, "Concentration"):
        string = string[:string.index("Concentration")-1]
    return string

    


#------------------------------------------METHODS TO CLEAN SCRAPPED DATA--------------------------------------

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

    # support vars for looping
    seqFlag = False
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
            elif has_identifier(courses[i], "elective"): #step 6 check if the course has elective in it
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

                        specialString = courses[i][:courses[i].find("elective")-1]

                        coursesParsed.append("Elective") 
                        creditsParsed.append(credits[i])
                        descriptionsParsed.append(specialString)
            elif "concentration" in courses[i]:
                concBoolean = True
                concCredits = credits[i]
                concDF = getConcentration(dfList)
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
    displayDF(concDF)

    if concBoolean:
        for i in range(len(concDF.index)):
            for j in range(len(concDF.loc[i, "Concentration"].loc[:,"Sequence"].index)):
                if checkForNoCredits(concDF.loc[i, "Concentration"].loc[j, "Credits"]):
                    concDF.loc[i, "Concentration"].loc[j, "Credits"] = course_dictionary[concDF.loc[i, "Concentration"].loc[j, "Sequence"]].getCredits()       
                concDF.loc[i, "Concentration"].loc[j, "Sequence"] = s(concDF.loc[i, "Concentration"].loc[j, "Sequence"])
        return d(seqArray, creditsParsed, descriptionsParsed, flagParsed, concDF, concCredits)
        # unused code
        
    
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

#-----------------------------------------------------------------------------------------------------


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

def recurssionIsTrash(array):
    for a in array:
        prereqCycle(a)
          
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

def prereqDictionaryFill(df: pd.DataFrame):
    for i in range(len(df.index)):
        seqArray = df.loc[i,"Sequence"]
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

# changew by adding 10 and use 1 less global
def filterPrereqDictionary(df: pd.DataFrame):
    filteredPrequistes = pd.DataFrame({'Courses':[], 'Value':[], 'Taken':[]})
    for i in range(len(df.index)):
        seqArray = df.loc[i,"Sequence"]
        for seq in seqArray.getSequence():
            courseArray = seq.iterateThroughArray()
            for course in courseArray:
                try:
                    if course != "Elective":
                        filteredPrequistes.loc[len(filteredPrequistes.index)] = [str(course).strip() , course_int_dictionary[str(course).strip()], False]
                except KeyError:
                    pass
    #filteredPrequistes.columns = ['Courses', 'Credits']
    return filteredPrequistes

def intergrateAviability(df: pd.DataFrame, quarter):
    
    for i in range(len(df.index)):
        try:
            courseName = str(df.loc[i,"Subject Code"]) + " " + str(df.loc[i, "Course No."])
            course_dictionary[courseName.replace("\xa0", " ")].setAviabilityTrue(quarter)
        except KeyError:
            pass
    
#-----------------------------------------METHODS FOR DEBUGGING--------------------------------------------


def displayDF(df):
     with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(df)
        print("printed")          

def printList(list):
    for item in list:
        print(item)

def convertCSVToCourseObject():
   #df = pd.read_csv("in.csv",converters={"Col3": literal_eval})
    
    df = pd.read_csv("courseObjects2.csv",converters={3:literal_eval})

    #df = pd.read_csv("courseObjects.csv") 
    df.columns = ['Courses', 'Credits', 'Prereqs', "Avail"]
    for i in range(len(df.index)):
        if pd.notna(df.loc[i,"Prereqs"]):
            course_dictionary[df.loc[i, "Courses"]] = c(df.loc[i, "Courses"], df.loc[i, "Credits"], df.loc[i, "Prereqs"], df.loc[i, "Avail"])
        else:
            course_dictionary[df.loc[i, "Courses"]] = c(df.loc[i, "Courses"], df.loc[i, "Credits"], "", df.loc[i, "Avail"])

def convertCourseObjectToCSV():
    filename = 'courseObjects2.csv'
    try:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            for key in course_dictionary:
                courseObj = course_dictionary[key]
                if isinstance(courseObj.getPrereqString(), type(None)) or courseObj.getPrereqString() == "":
                    writer.writerow([cleanWIFormating(courseObj.getCourseName()), courseObj.getCredits(), "", courseObj.getAvial()])
                else:
                    writer.writerow([cleanWIFormating(courseObj.getCourseName()), courseObj.getCredits(), courseObj.getPrereqString(), courseObj.getAvial()])

    except BaseException as e:
        print('BaseException:', filename)

def cleanWIFormating(string)->str:
        # CS 26   [WI]
        while(has_identifier(string, "  ")):
            string = string.replace("  "," ")    
        return string

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

def assignPredeterminedCourse(course: str, df: pd.DataFrame)->pd.DataFrame:
    for i in range(len(df.index)):
        if df.loc[i, "Courses"] == course:
            df.loc[i, "Taken"] = True
            return df
    # if it makes it here the course is not in the dataframe so add it

    df.loc[len(df.index)] = [str(course).strip(), 0, True]
    return df

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
            print(str(miniCounter)+"." + classes)  
            miniCounter += 1     
        counter+= 1

if __name__ == '__main__':
    
    # -------SCRAPING----------
    #scrapeCourseCatalog()
    #scrapeTermMaster()
    #convertCourseObjectToCSV()

    #-----Not Scraping-----
    convertCSVToCourseObject()
    
    course_dictionary_2 = {}
    
    NAME = "CS" # temp var
    COLLEGE = "CCI"
    ## modification ends

    list_degree_frame = parseDegreeRequiremnts(NAME)
    degreeReq = parseThroughClasses(list_degree_frame)
    degreeReq.setDegreeName(NAME)
    degreeReq.setDegreeCollege(COLLEGE)
    print(degreeReq)

    # TEMP HARD CODED DETERIMENES SCIENCE SEQUENCE
    SEQUENCELOCK = "PHYS"
    degreeReq.selectScienceSequence(SEQUENCELOCK)

    prereqDictionaryFill(degreeReq.getDegree())
    concDf = degreeReq.selectConcentration("Algorithms and Theory")
    prereqDictionaryFill(concDf)

    filteredDataFrame = filterPrereqDictionary(degreeReq.getMegaDegreeRequirments())

    # TEMP VARs

    if degreeReq.getDegreeCollege() == "CCI":
        numberOfQuarters = 18
        springSummerCoop = True
        coopNumber = 3
        numTermsPremade = 1
        creditMin = 15
        creditMax = 17

        numberOfFalls = 5
        numberOfWinters = 5
        numberOfSprings = 5
        numberOfSummers = 5
        

        if springSummerCoop:
            numberOfSprings = 2
            numberOfSummers = 0
        else:
            numberOfFalls = 2
            numberOfWinters = 2
            numberOfSummers = 3

        posArray = [] #array that contains the plan of study
        for i in range(numberOfQuarters):
            posArray.append([])
        numberOfArray = [numberOfFalls, numberOfWinters, numberOfSprings, numberOfSummers]
        coopBoolean = False
        firstYear = True
        
        
      

        # -------- pre decided terms -----------------
        firstTermPremade = True
        predetiermendCourses = ["CS 164", "PSY 101", "MATH 121", "ENGL 101", "CI 101"]
        for i in range(numTermsPremade):
            if i == 0 and firstTermPremade:
                posArray[i].append("UNIV CI101")

                for course in predetiermendCourses:
                    posArray[i].append(course)
                    filteredDataFrame = assignPredeterminedCourse(course, filteredDataFrame)
            degreeReq.checkCompletion(filteredDataFrame)




        displayDF(filteredDataFrame)
        for i in range(numTermsPremade, numberOfQuarters):
            year = 1
            totalQuarterAvail = calculateQuarterlyAvail(filteredDataFrame)
            #totalQuarterSingularAvail = calculateQuarterlySingularAvail(filteredDataFrame)
            term = i
            credits = 0.0
            #for QuarterAvail in totalQuarterAvail:
            #   print("A "+str(QuarterAvail))
            #   print("S "+str(totalQuarterSingularAvail))
            if term > 3:
                firstYear = False
                while term > 3:
                    term -= 4
                    year += 1

                if coopNumber == 1 and year == 3:
                    coopBoolean = coopBooleanFinder(springSummerCoop, term)
                elif coopNumber == 3 and (year == 2 or year == 3 or year == 4):
                    coopBoolean = coopBooleanFinder(springSummerCoop, term)
                else:
                    coopBoolean = False

            if term == 0:
                #print("Fall") # fall
                if coopBoolean:
                 #   print("\tCO-OP")
                    posArray[i-1].append("COOP 201")
                else:
                    pass
                    while(creditMin > credits):
                        course = "Temp Empty"
                        max = 0
                        pos = 1
                        for j in range(len(filteredDataFrame.index)):
                            if not filteredDataFrame.loc[j, "Taken"]:
                                if not degreeReq.getTaken(filteredDataFrame.loc[j, "Courses"]):
                                    tempMax = filteredDataFrame.loc[j, "Value"]
                                    if tempMax > max:
                                        course = filteredDataFrame.loc[j, "Courses"]
                                        pos = j
                                        max = tempMax
                                    

                        posArray[i].append(course)
                        filteredDataFrame.loc[pos, "Taken"] = True
                        credits += float(course_dictionary[course].getCredits())
                        degreeReq.checkCompletion(filteredDataFrame)

            elif term == 1:
                #print("Winter") # winter
                if coopBoolean:
                 #   print("\tCO-OP")
                    posArray[i-1].append("COOP 201")
            elif term == 2:
                #print("Spring") # spring
                if coopBoolean:
                 #   print("\tCO-OP")
                    posArray[i-1].append("COOP 201")
            elif term == 3 and not firstYear:
                #print("Summer") # summer
                if coopBoolean:
                 #   print("\tCO-OP")
                    posArray[i-1].append("COOP 201")

        printPlanOfStudy(posArray)
        
       



# no pre reqs shows up as ""
    




  



    
    
#------------------------------- EVERYTHING BELLOW IS TEMPORARLIY UNUSED PLEASE IGNORE----------------------------------------------
