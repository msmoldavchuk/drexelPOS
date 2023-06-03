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

course_dictionary = {}

keyword_descriptor = {
        "Computer" : "CS",
        "Data Science": "DS", 
        "Software": "SE", 
        "Computing": "CI", 
        "Information": "IS", 
        "Science": "SCI", 
        "Mathematics":"MTH",
        "Humanities": "HUM", 
        "University": "UNV", 
        "Statistics": "STAT",
        "Programming": "PRG",
        "Business": "BSN",
        "Liberal Studies": "LS",
        "Economics": "ECON",
        "General Education": "GED",
        "English": "ENG",
        "Communication": "COM",

    }

LOC = ["Arts and Sciences","Bennett S. LeBow Coll. of Bus.","Center for Civic Engagement","Close Sch of Entrepreneurship","Col of Computing & Informatics","College of Engineering","Dornsife Sch of Public Health","Goodwin Coll of Prof Studies","Graduate College", "Miscellaneous","Nursing & Health Professions","Pennoni Honors College","Sch.of Biomed Engr,Sci & Hlth","School of Education","Thomas R. Kline School of Law"]

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


def getMinors():
    listUrl = getUrlsMinors()
    listMinorsDf = [[],[]]
    for url in listUrl:
        try:
            course_catalog = requests.get(url).text
            parsed_course_catalog = BeautifulSoup(course_catalog, 'html.parser')
            title_parsed = parsed_course_catalog.find(class_='page-title').text
            course_list = parsed_course_catalog.find_all('table', class_='sc_courselist')
            df = pd.read_html(str(course_list))[0]   

            df.columns = ['Courses', 'Label', 'Credits']
            listMinorsDf[0].append(df)
            listMinorsDf[1].append(title_parsed)
        except:
            print("*")
            print(url)

    return listMinorsDf

def getMinorsTESTING(indexArray):
    listUrl = getUrlsMinors()
    listMinorsDf = []
    while True:
        for i in indexArray:
            try:
                course_catalog = requests.get(listUrl[i]).text
                parsed_course_catalog = BeautifulSoup(course_catalog, 'html.parser')
                title_parsed = parsed_course_catalog.find(class_='page-title').text
                course_list = parsed_course_catalog.find_all('table', class_='sc_courselist')
                df = pd.read_html(str(course_list))[0]   
                df.columns = ['Courses', 'Label', 'Credits']
                print(title_parsed)
                listMinorsDf.append(df)
            except:
                print("*")
                print(listUrl[i])
        break

    return listMinorsDf

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
def getUrlsMinors() -> list:
    listofUrls = []
    html = requests.get("https://catalog.drexel.edu/minors/undergraduate/").text

    parsed_course_catalog = BeautifulSoup(html, 'html.parser')
    parsed_course_catalog = parsed_course_catalog.find_all('div', class_="tab_content", id ="textcontainer")
    #the two list


    for list_courses in parsed_course_catalog:
        #urls in each list
        div_list_courses_p = list_courses.find_all('p')
        for pItem in div_list_courses_p:
            urls = pItem.find_all('a')
            for url in urls:
                print("https://catalog.drexel.edu" + url.get('href'))
                listofUrls.append("https://catalog.drexel.edu" + url.get('href'))
    return listofUrls

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
def getConcentration(dfList, name = "")->pd.DataFrame:
    concentrationList = [[],[]]
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
        numParsed = []


        gatheredData = {"CS":3}
        try:
            num = gatheredData[name]
        except:
            num = 0
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
                    numParsed.append(num)
            elif len(courses[i]) <= strlength and has_identifier(courses[i], "Digit"):
                coursesParsed.append(courses[i])
                creditsParsed.append(credits[i])
                numParsed.append(num)
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
                dfPart = pd.DataFrame({"Sequence": coursesParsed, "Credits": creditsParsed, "Type": descriptionsParsed, "Flag": flagParsed,"Num":numParsed, "Taken": False})
                coursesParsed = []
                creditsParsed = []
                descriptionsParsed = []
                flagParsed = []
                numParsed = []
                
                concentrationList[0].append(dfPart)
                concentrationList[1].append(descriptorRequired)
                descriptorRequired = filterDescription(courses[i])


    
        dfPart = pd.DataFrame({"Sequence": coursesParsed, "Credits": creditsParsed, "Type": descriptionsParsed, "Flag": flagParsed, "Num":numParsed, "Taken": False})
        concentrationList[0].append(dfPart)
        concentrationList[1].append(descriptorRequired)        
    return concentrationList

# A means of filtering the description for the concentrartion
# it is sent a string and then returns the string containing everything before for "Concentration"
def filterDescription(string):
    if has_identifier(string, "Concentration"):
        string = string[:string.index("Concentration")-1]
    return string

    
def processMinors(listMinors):
    minorsList = []
    for minor in listMinors:
        coursesUnproccesed = list(minor.loc[:,"Courses"])
        credits = list(minor.loc[:,"Credits"])
        courses = []
        
        for course in coursesUnproccesed:
            if pd.notna(course):
                courses.append(course.replace("\xa0", " "))
            else:
                pass


        coursesParsed = []
        creditsParsed = []
        descriptionsParsed = []
        flagParsed = [] # 0 = no problem, 1 = elective, 2 = mandatory
        numParsed = []

        electiveReqsDictonary = {}
        
        seqFlag = False
        selectFlag = False
        choseFlag = False
        requirmentFlag = False
        trackFlag = False
        newTrack = True
        track2 = True
        prereqFlag = False


        descriptorRequired = ""
        numberNeeded = 0
        inc = 1
        strlength = 13



        for i in range(0, len(courses)):
            descriptorRequired = keyWordSearcher(courses[i], descriptorRequired) #step 1 check the type of course i.e cs or se
            if checkForNoCredits(credits[i]) and i >= 1:   #step 2 check if the credits exist if not then get previous
                credits[i] = credits[i-inc]
            #courses[i] = cleanBrackets(courses[i])
  
            if selectFlag == True or choseFlag == True:
                if(courses[i][0:2] == "or"):
                    if len(courses[i]) > 5:
                        ns = str(coursesParsed[len(coursesParsed)-1]) + " | " + str(courses[i])[3:]         #take previous parsed and add to the new line    
                        coursesParsed[len(coursesParsed)-1] = ns
                        descriptionsParsed[len(descriptionsParsed)-1] = descriptorRequired
                        flagParsed[len(flagParsed)-1] = 6 + 1
                        numParsed[len(numParsed)-1] = numberNeeded
                    else:
                        pass #causes class \n or \n class to not process
                elif ((len(courses[i]) <= strlength and has_identifier(courses[i], "Digit"))): #step 5 look for courses
                    try:
                        if flagParsed[-1] == (6 + 1):
                            ns = str(coursesParsed[len(coursesParsed)-1]) + " ^ " + str(courses[i])         #take previous parsed and add to the new line    
                            coursesParsed[len(coursesParsed)-1] = ns
                            descriptionsParsed[len(descriptionsParsed)-1] = descriptorRequired
                            flagParsed[len(flagParsed)-1] = 6 + 1
                            numParsed[len(numParsed)-1] = numberNeeded
                        elif flagParsed[-1] == 1:
                            coursesParsed[-1] = courses[i]
                            creditsParsed[-1] = credits[i]
                            flagParsed[-1] = 6 + 1 # offset to not chain seq
                            numParsed[-1] = numberNeeded
                            descriptionsParsed[-1] = descriptorRequired
                        else:
                            coursesParsed.append(courses[i])
                            creditsParsed.append(credits[i])
                            numParsed.append(numberNeeded)
                            flagParsed.append(6 + 1) # 6 = sel flag
                            descriptionsParsed.append(descriptorRequired)
                    except:
                        coursesParsed.append(courses[i])
                        creditsParsed.append(credits[i])
                        numParsed.append(numberNeeded)
                        flagParsed.append(6 + 1) # 6 = sel flag
                        descriptionsParsed.append(descriptorRequired)
                else:
                    flagParsed[-1] = 6 # makes it 6
                    selectFlag = False
                    choseFlag = False
            elif prereqFlag:
                if(courses[i][0:2] == "or"):
                   pass
                elif ((len(courses[i]) <= strlength and has_identifier(courses[i], "Digit"))): #step 5 look for courses
                    pass
                else:
                    prereqFlag = False
            elif not seqFlag and not selectFlag and not choseFlag and not requirmentFlag and not trackFlag: # step 3 check if sequence mode
                # NOT A SEQUENCE

                if courses[i][0:2] == "or": # step 4 check if the course contains or
                    coursesParsed[len(coursesParsed)-1] = coursesParsed[len(coursesParsed)-1] + " | " + courses[i][3:len(courses[i])]
                    descriptionsParsed[len(descriptionsParsed)-1] = descriptorRequired
                    flagParsed[len(flagParsed)-1] = 4 #adds 4 for or flag
                    numParsed[len(numParsed)-1] = 0
                elif (len(courses[i]) <= strlength and has_identifier(courses[i], "Digit")) or ("&" in courses[i] and len(courses[i]) <= strlength): #step 5 check if the course is type ABC123
                    if has_identifier(courses[i],"*"):
                        coursesParsed.append(courses[i][:len(courses[i])])
                        creditsParsed.append(credits[i])
                        descriptionsParsed.append(descriptorRequired)
                        flagParsed.append(2)
                        numParsed.append(0)
                    else:
                        coursesParsed.append(courses[i])
                        creditsParsed.append(credits[i])
                        descriptionsParsed.append(descriptorRequired)
                        flagParsed.append(0)
                        numParsed.append(0)
                elif "sequences:" in courses[i]: #step 7 check if a sequence is comming up
                    seqFlag = True  # if yes change modes
                elif ("Required" in courses[i] and not "Courses" in courses[i]) or "required" in courses[i]:
                    requirmentFlag = True
                    rFlip = False
                elif ("select" in courses[i] or "Select" in courses[i]) and len(courses[i]) < 240:
                    listExpression = re.findall("[A-Z][A-Z][A-Z][A-Z],|[A-Z][A-Z][A-Z],|[A-Z][A-Z],|[A-Z][A-Z][A-Z][A-Z]\)|[A-Z][A-Z][A-Z]\)|[A-Z][A-Z]\)|[A-Z][A-Z][A-Z][A-Z]\.|[A-Z][A-Z][A-Z]\.|[A-Z][A-Z]\.", courses[i])
                    # SPECIAL CASE where an elective functions as a select
                    if listExpression:
                        for j in range(len(listExpression)):
                            listExpression[j] = listExpression[j][0:len(listExpression[j])-1]
                        numberNeeded = numFinder(courses[i])
                        electiveReqsDictonary[descriptorRequired] = listExpression
                        if flagParsed[-1] != 1:
                            coursesParsed.append("elective")
                            creditsParsed.append(credits[i])
                            descriptionsParsed.append(reverseKeyWordSearcher(descriptorRequired))
                            flagParsed.append(1)
                            numParsed.append(0)
                    else:
                        numberNeeded = numFinder(courses[i])
                        selectFlag = True
                elif "track" in courses[i]:
                    trackFlag = True
                    newTrack = True
                elif "choose" in courses[i] or "Choose" in courses[i]  or "Complete" in courses[i] or "Take" in courses[i]:
                    choseFlag = True
                elif has_identifier(courses[i], "elective") or has_identifier(courses[i], "Elective"): #step 6 check if the course has elective in it
                        flagParsed.append(1) #elective flag
                        numParsed.append(0)                        
                        if has_identifier(courses[i], "elective"):
                            specialString = courses[i][:courses[i].find("elective")-1]
                        else:
                            specialString = courses[i][:courses[i].find("Elective")-1]

                        coursesParsed.append("Elective") 
                        creditsParsed.append(credits[i])
                        descriptionsParsed.append(specialString)
                elif "Required Pre-requisites" in courses[i]:
                    prereqFlag = False
            elif seqFlag == True: #step 4 sequence procedure activated 
                if ((len(courses[i]) <= strlength and has_identifier(courses[i], "Digit")) or has_identifier(courses[i], "&")): #step 5 look for courses
                    if flagParsed[-1] == 3:
                        ns = str(coursesParsed[len(coursesParsed)-1]) + " ^ " + str(courses[i])         #take previous parsed and add to the new line    
                        coursesParsed[len(coursesParsed)-1] = ns
                        descriptionsParsed[len(descriptionsParsed)-1] = descriptorRequired
                        flagParsed[len(flagParsed)-1] = 3
                        numParsed[len(numParsed)-1] = 0
                    else:
                        coursesParsed.append(courses[i])
                        creditsParsed.append(credits[i])
                        flagParsed.append(3)
                        descriptionsParsed.append(descriptorRequired)
                        numParsed.append(0)

                elif courses[i][0:2].lower() == "or": #step 6 look for or keyword *different than prior
                    #Sequence ors get their own line
                    i += 1 #skip current line and go to next one
                    inc = 2  # ancounts for skip in line                                                    
                    ns = str(coursesParsed[len(coursesParsed)-1]) + " ^ " + str(courses[i])         #take previous parsed and add to the new line    
                    coursesParsed[len(coursesParsed)-1] = ns
                    descriptionsParsed[len(descriptionsParsed)-1] = descriptorRequired
                    flagParsed[len(flagParsed)-1] = 3 # 3 = sequence flag 
                    numParsed[len(numParsed)-1] = 0
                                        
                elif has_identifier(courses[i], "elective"): #step 7 looks for electives
                    specialString = courses[i][:courses[i].find("elective")-1]
                    coursesParsed.append("Elective")
                    creditsParsed.append(credits[i])
                    descriptionsParsed.append(specialString)
                    flagParsed.append(1)
                    numParsed.append(0)

                    seqFlag = False       # elective marks end of sequence         
                else:
                    inc = 1
                    seqFlag = False #emergancy way to end sequence
            elif trackFlag == True:
                if "track" in courses[i] or "Track" in courses[i]:
                    if newTrack == False:
                        track2 = True
                elif ((len(courses[i]) <= strlength and has_identifier(courses[i], "Digit"))):
                    if newTrack: 
                        print("!" + courses[i])
                        coursesParsed.append(courses[i])
                        creditsParsed.append(credits[i])
                        flagParsed.append(3)
                        descriptionsParsed.append(descriptorRequired)
                        numParsed.append(0)
                        newTrack = False
                    elif track2:
                        ns = str(coursesParsed[len(coursesParsed)-1]) + " " + str(courses[i])         #take previous parsed and add to the new line    
                        coursesParsed[len(coursesParsed)-1] = ns
                        descriptionsParsed[len(descriptionsParsed)-1] = descriptorRequired
                        flagParsed[len(flagParsed)-1] = 3
                        numParsed[len(numParsed)-1] = 0
                        track2 = False
                    else:
                        ns = str(coursesParsed[len(coursesParsed)-1]) + " | " + str(courses[i])         #take previous parsed and add to the new line    
                        coursesParsed[len(coursesParsed)-1] = ns
                        descriptionsParsed[len(descriptionsParsed)-1] = descriptorRequired
                        flagParsed[len(flagParsed)-1] = 3
                        numParsed[len(numParsed)-1] = 0
                elif courses[i][0:2].lower() == "or": #step 6 look for or keyword *different than prior
                    #Sequence ors get their own line                                          
                    ns = str(coursesParsed[len(coursesParsed)-1]) + " ^ "       #take previous parsed and add to the new line    
                    coursesParsed[len(coursesParsed)-1] = ns
                    descriptionsParsed[len(descriptionsParsed)-1] = descriptorRequired
                    flagParsed[len(flagParsed)-1] = 3 # 3 = sequence flag 
                    numParsed[len(numParsed)-1] = 0
                else:
                    trackFlag = False
            elif requirmentFlag == True:
                if ((len(courses[i]) <= strlength and has_identifier(courses[i], "Digit")) or has_identifier(courses[i], "&")):
                    if rFlip == False: 
                        print("!" + courses[i])
                        coursesParsed.append(courses[i])
                        creditsParsed.append(credits[i])
                        flagParsed.append(3)
                        descriptionsParsed.append(descriptorRequired)
                        numParsed.append(0)
                        rFlip = True
                    else:
                        ns = str(coursesParsed[len(coursesParsed)-1]) + " ^ " + str(courses[i])         #take previous parsed and add to the new line    
                        coursesParsed[len(coursesParsed)-1] = ns
                        descriptionsParsed[len(descriptionsParsed)-1] = descriptorRequired
                        flagParsed[len(flagParsed)-1] = 3
                        numParsed[len(numParsed)-1] = 0
                elif courses[i][0:2].lower() == "or": #step 6 look for or keyword *different than prior
                    #Sequence ors get their own line
                    i += 1 #skip current line and go to next one
                    inc = 2  # ancounts for skip in line                                                    
                    ns = str(coursesParsed[len(coursesParsed)-1]) + " ^ "       #take previous parsed and add to the new line    
                    coursesParsed[len(coursesParsed)-1] = ns
                    descriptionsParsed[len(descriptionsParsed)-1] = descriptorRequired
                    flagParsed[len(flagParsed)-1] = 3 # 3 = sequence flag 
                    numParsed[len(numParsed)-1] = 0
                elif "select" in courses[i] or "Select" in courses[i]:
                    listExpression = re.findall("[A-Z][A-Z][A-Z][A-Z],|[A-Z][A-Z][A-Z],|[A-Z][A-Z],|[A-Z][A-Z][A-Z][A-Z]\)|[A-Z][A-Z][A-Z]\)|[A-Z][A-Z]\)|[A-Z][A-Z][A-Z][A-Z]\.|[A-Z][A-Z][A-Z]\.|[A-Z][A-Z]\.", courses[i])
                    # SPECIAL CASE where an elective functions as a select
                    if listExpression:
                        for j in range(len(listExpression)):
                            listExpression[j] = listExpression[j][0:len(listExpression[j])-1]
                        numberNeeded = numFinder(courses[i])
                        electiveReqsDictonary[descriptorRequired] = listExpression
                        if flagParsed[-1] != 1:
                            coursesParsed.append("elective")
                            creditsParsed.append(credits[i])
                            descriptionsParsed.append(reverseKeyWordSearcher(descriptorRequired))
                            flagParsed.append(1)
                            numParsed.append(0)
                    else:
                        numberNeeded = numFinder(courses[i])
                        selectFlag = True
                elif "track" in courses[i]:
                    trackFlag = True
                    newTrack = True
                elif "choose" in courses[i] or "Choose" in courses[i]:
                    choseFlag = True
                elif has_identifier(courses[i], "elective") or has_identifier(courses[i], "Elective"): #step 6 check if the course has elective in it
                        flagParsed.append(1) #elective flag
                        numParsed.append(0)                        
                        if has_identifier(courses[i], "elective"):
                            specialString = courses[i][:courses[i].find("elective")-1]
                        else:
                            specialString = courses[i][:courses[i].find("Elective")-1]

                        coursesParsed.append("Elective") 
                        creditsParsed.append(credits[i])
                        descriptionsParsed.append(specialString)
                elif "required" in courses[i]:
                    requirmentFlag = True
                    rFlip = False
                else:
                    requirmentFlag = False
        seqArray = []
        for course in coursesParsed:
            seqArray.append(s(course))
        minorsList.append(pd.DataFrame({"Sequence":seqArray, "Credits": creditsParsed, "Type": descriptionsParsed, "Flag": flagParsed, "Num": numParsed, "Taken": False}))
        
    return minorsList
            
def storeMinor(dfList, namesList):
    nameDict = {}
    for i in range(len(dfList)):
        dfList[i].to_csv("Minor" + str(i)  + ".csv",index=False)
        nameDict[namesList[i]] = i

    csv_file = "NamesForMinors.csv"

    with open(csv_file, "w", newline = "") as file:
        writer = csv.writer(file)
        for keyVal in enumerate(nameDict):
            writer.writerow(keyVal)



def spMinors():
    output = getMinors()
    
    processedMinors = processMinors(output[0])
    storeMinor(processedMinors, output[1])
    

def readMinors():
    minorsDictonary = {}
    with open('NamesForMinors.csv') as csvfile:
        for number, minor in csv.reader(csvfile):
            minorsDictonary[minor] = pd.read_csv("Minor" + number + ".csv")
    return minorsDictonary

#------------------------------------------METHODS TO CLEAN SCRAPPED DATA--------------------------------------

# Filters through scrapped degree data 
# Paramater is a list of dataframes formated with ("Courses", "Credits")
# returns a degree object
def parseThroughClasses(dfList, name = "CS")-> d: 

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
    numParsed = []


    electiveReqsDictonary = {}

    # support vars for looping
    seqFlag = False
    selectFlag = False
    choseFlag = False
    chooseSeqCounter = 2
    decrementSeqFlag = False
    descriptorRequired = ""
    numberNeeded = 0
    inc = 1
    myiter = iter(range(0, len(courses)))
    strlength = 15 #temp value
    
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
            print(""+courses[i])
            if ((len(courses[i]) <= strlength and has_identifier(courses[i], "Digit"))): #step 5 look for courses
                if flagParsed[-1] == 6:
                    ns = str(coursesParsed[len(coursesParsed)-1]) + " | " + str(courses[i])         #take previous parsed and add to the new line    
                    coursesParsed[len(coursesParsed)-1] = ns
                    descriptionsParsed[len(descriptionsParsed)-1] = descriptorRequired
                    flagParsed[len(flagParsed)-1] = 6
                    numParsed[len(numParsed)-1] = numberNeeded
                elif flagParsed[-1] == 1:
                    coursesParsed[-1] = courses[i]
                    creditsParsed[-1] = credits[i]
                    flagParsed[-1] = 6
                    numParsed[-1] = numberNeeded
                    descriptionsParsed[-1] = descriptorRequired
                else:
                    coursesParsed.append(courses[i])
                    creditsParsed.append(credits[i])
                    numParsed.append(numberNeeded)
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
                numParsed[len(numParsed)-1] = 0
            elif len(courses[i]) <= strlength and has_identifier(courses[i], "Digit"): #step 5 check if the course is type ABC123
                if has_identifier(courses[i],"*"):
                    coursesParsed.append(courses[i][:len(courses[i])])
                    creditsParsed.append(credits[i])
                    descriptionsParsed.append(descriptorRequired)
                    flagParsed.append(2)
                    numParsed.append(0)
                else:
                    coursesParsed.append(courses[i])
                    creditsParsed.append(credits[i])
                    descriptionsParsed.append(descriptorRequired)
                    flagParsed.append(0)
                    numParsed.append(0)
            elif "concentration" in courses[i]:
                concBoolean = True
                concCredits = credits[i]
                concList = getConcentration(dfList, name)
            elif "sequences" in courses[i] or "sequence" in courses[i] or "Sequence" in courses[i]: #step 7 check if a sequence is comming up
                seqFlag = True  # if yes change modes
                chooseSeqCounter = 2
            elif "select" in courses[i] or "Select" in courses[i]:
                listExpression = re.findall("[A-Z][A-Z][A-Z][A-Z],|[A-Z][A-Z][A-Z],|[A-Z][A-Z],|[A-Z][A-Z][A-Z][A-Z]\)|[A-Z][A-Z][A-Z]\)|[A-Z][A-Z]\)|[A-Z][A-Z][A-Z][A-Z]\.|[A-Z][A-Z][A-Z]\.|[A-Z][A-Z]\.", courses[i])
                # SPECIAL CASE where an elective functions as a select
                if listExpression:
                    for j in range(len(listExpression)):
                        listExpression[j] = listExpression[j][0:len(listExpression[j])-1]
                    
                    numberNeeded = numFinder(courses[i])
                    electiveReqsDictonary[descriptorRequired] = listExpression
                    if flagParsed[-1] != 1:
                        coursesParsed.append("elective")
                        creditsParsed.append(credits[i])
                        descriptionsParsed.append(reverseKeyWordSearcher(descriptorRequired))
                        flagParsed.append(1)
                        numParsed.append(0)

                else:
                    numberNeeded = numFinder(courses[i])

                    selectFlag = True
            elif has_identifier(courses[i], "elective") or has_identifier(courses[i], "Elective"): #step 6 check if the course has elective in it
                    flagParsed.append(1) #elective flag
                    numParsed.append(0)

                    if(has_identifier(courses[i], "Free")): #free electives = end of program
                        coursesParsed.append("Elective")
                        creditsParsed.append(credits[i]) 
                        descriptionsParsed.append("Special") #special internal descriptor 

                        flagParsed.append(1)
                        numParsed.append(0)

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
                    numParsed[len(numParsed)-1] = 0
                else:
                    coursesParsed.append(courses[i])
                    creditsParsed.append(credits[i])
                    flagParsed.append(3)
                    descriptionsParsed.append(descriptorRequired)
                    numParsed.append(0)

            elif courses[i][0:2].lower() == "or": #step 6 look for or keyword *different than prior
                #Sequence ors get their own line
                i += 1 #skip current line and go to next one
                inc = 2  # ancounts for skip in line                                                    
                ns = str(coursesParsed[len(coursesParsed)-1]) + " ^ " + str(courses[i])         #take previous parsed and add to the new line    
                coursesParsed[len(coursesParsed)-1] = ns
                descriptionsParsed[len(descriptionsParsed)-1] = descriptorRequired
                flagParsed[len(flagParsed)-1] = 3 # 3 = sequence flag 
                numParsed[len(numParsed)-1] = 0
                                       
                next(myiter, None) #iterates loop   
                """
                Sample
                Phys 101
                or
                Chem 101
                get to or and skip to chem 101
                Take phys 101 and combine w/ "^" in between
                """                                            
            elif  "sequence" in courses[i]  or "sequences" in courses[i] or "seqence" in courses[i]:
                       # won't pick up right number
                print("HELLO")
                decrementSeqFlag = True
            elif has_identifier(courses[i], "elective"): #step 7 looks for electives
                specialString = courses[i][:courses[i].find("elective")-1]
                coursesParsed.append("Elective")
                creditsParsed.append(credits[i])
                descriptionsParsed.append(specialString)
                flagParsed.append(1)
                numParsed.append(0)

                seqFlag = False       # elective marks end of sequence  
           
                
            else:
                inc = 1
                seqFlag = False #emergancy way to end sequence

            if decrementSeqFlag and chooseSeqCounter != 0:
                chooseSeqCounter -= 1
            elif chooseSeqCounter == 0:
                seqFlag = False

    # final step

    
    seqArray = []
    for course in coursesParsed:
        seqArray.append(s(course)) #convert filtered courses into array of sequence objects
    # concentrations
    #displayDF(concDF)

    if concBoolean:
        for i in range(len(concList[1])):
            for j in range(len(concList[0][i].loc[:,"Sequence"].index)):
                if checkForNoCredits(concList[0][i].loc[j, "Credits"]):
                    concList[0][i].loc[j, "Credits"] = course_dictionary[concList[0][i].loc[j, "Sequence"]].getCredits()       
                concList[0][i].loc[j, "Sequence"] = s(concList[0][i].loc[j, "Sequence"])
        return d(seqArray, creditsParsed, descriptionsParsed, flagParsed,numParsed, concList, concCredits, requiredConcentration=True, requiredMinor=False)
        
    
    # make and return degree object
    return d(seqArray, creditsParsed, descriptionsParsed, flagParsed ,numParsed)    

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
    
def numFinder(string:str):
    dictNumbers = {"one":1,
                   "two":2,
                   "three":3,
                   "four":4,
                   "five":5,
                   "six":6,
                   "seven":7,
                   "eight":8,
                   "nine":9}
    for key in dictNumbers.keys():
        if key in string.lower():
            return dictNumbers[key] 
    return 0

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
