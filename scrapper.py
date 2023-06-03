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
# html5lib
import scraper

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


#creditsInWrongPlaceBoolean = False

FRESHMAN = 0
SOPHMORE = 40
PREJUNIOR = 70.5
JUNIOR = 96.5
SENIOR = 130

#---------------------------------------METHODS TO SCRAPE DATA----------------------------------------
# This function takes in a course html and prints out the course id and name




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
def createPlan(name, degreeReq, filteredDataFrame, NUMBEROFQUARTERS = 18, SPRINGSUMMERCOOP =  True, CREDITGOAL = 15, COOPNUMBER = 3):
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
        if name == "CS" or name == "SE":
            predetiermendCourses = ["CS 164", "PSY 101", "MATH 121", "ENGL 101", "CI 101"]
        elif name == "CST":
            predetiermendCourses = ["INFO 151", "PSY 101", "MATH 121", "ENGL 101", "CI 101"]
        else:
            predetiermendCourses = ["INFO 101", "PSY 101", "MATH 121", "ENGL 101", "CI 101"]

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
    scraper.convertCSVToCourseObject()
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
    posArray = createPlan(NAME, degreeReq, filteredDataFrame,  NUMBEROFQUARTERS, SPRINGSUMMERCOOP, CREDITGOAL, COOPNUMBER)
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

def scrapingDegree(NAME)->d:
    scraper.convertCSVToCourseObject()
    list_degree_frame = scraper.parseDegreeRequiremnts(NAME)
    degreeReq = scraper.parseThroughClasses(list_degree_frame)
    return degreeReq


#------------------------------- EVERYTHING BELLOW IS "Main"----------------------------------------------
if __name__ == "__main__":
    course_dictionary = scraper.course_dictionary 
    #electiveProcessing(process_requiremnt_html())
   

    #deg = scrapingDegree("EDS")
   # deg.convertDegreeToCSV("EDS")
    
    #print(deg.getConcentrationsTesting())
   # scrapingDegree("CST").convertDegreeToCSV("CST")
    #print(scrapingDegree("CST").getConcentrationsTesting())

    getPlanOfStudy(NAME = "EDS", SEQUENCES=[["CS 270", "CS 283"],["ECON 203", "ECON 344", "ECON 360"]], SPRINGSUMMERCOOP=False, CONCENTRATIONARRAY=[])
    
    #convertCSVToCourseObject()
    #list_degree_frame = parseDegreeRequiremnts("CS")
    #degreeReq = parseThroughClasses(list_degree_frame)
    #degreeReq.convertDegreeToCSV("CS")
    #print(degreeReq.getDataForWebsite())

    #degreeReq.convertDegreeToCSV("CS")
    #print(degreeReq)
    #getPlanOfStudy(NAME = "CS", SEQUENCES=["CHEM"],SPRINGSUMMERCOOP=True)

    

    
    #spMinors()
    #degreeReq = d()
   # degreeReq.convertDegreeToCSV("CS")
   # getPlanOfStudy(NAME = "SE", SEQUENCES=["BIO", ["ECON 201", "ECON 202"]] ,CONCENTRATIONARRAY=[],SPRINGSUMMERCOOP=True)

 
