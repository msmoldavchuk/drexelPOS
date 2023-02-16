import requests, html5lib
from bs4 import BeautifulSoup
import pandas as pd
import time
import sys
from selenium import webdriver

def traverseQuater(soup):
    lsitOfQuaters = []
    listUrlQ = []
    terms = soup.find_all("div", {"class": "term"})
    for term in terms:
        if len(lsitOfQuaters) == 1:
            break
        quater = term.find('a')
        lsitOfQuaters.append(quater)
    for quater in lsitOfQuaters:
        listUrlQ.append("https://termmasterschedule.drexel.edu" + quater.get('href'))
    return listUrlQ

def getListofDeparements(session):
    depList = []
    soup = BeautifulSoup(session.get('https://termmasterschedule.drexel.edu/webtms_du/').text, 'html.parser')

def traverseDeparement(quarter,session : requests.Session):
    listOfEndings = ["A" , "AS", "B","CV","C","CI", "E","PH","GC","GD","X","NH", "PE","R","T","L"]
    depList = []
    for ending in listOfEndings:
        soup = BeautifulSoup(s.get(quarter + ending).text, 'html.parser')
        time.sleep(.3)
        print(quarter + str(ending))
        depPannel = soup.find("table", {"class": "collegePanel"})
        try:
            departments = depPannel.find_all("class" == "odd")
            departments.append(depPannel.find_all("class" == "even"))
        except:
            print(quarter + str(ending) + " is empty")
            print(soup)
            sys.exit()
        for dep in departments:
            try:
                depList.append("https://termmasterschedule.drexel.edu" + dep.find('a').get('href'))
            except:
                continue
    return depList

def get_aval(dep, session : requests.Session):
    #headers = {'User-Agent': 'Mozilla/5.0'}
    #soup = BeautifulSoup(session.get(dep, timeout = 5, headers=headers).text, 'html.parser')
    #time.sleep(.5)
    #precursor = soup.find("td", {"align": "center"})
    #table = precursor.find_all("table","id"=="sortableTable")
    #while True:
        #soup = BeautifulSoup(session.get(dep, timeout = 5).text, 'html.parser')
        #time.sleep(.5)
        #precursor = soup.find("td", {"align": "center"})
        #table = precursor.find_all("table","id"=="sortableTable")
        
    driver = webdriver.Edge()
    #driver.add_cookie({"name": "JSESSIONID", "value": s.cookies.get_dict()["JSESSIONID"]})
    # Navigate to url
    driver.get(dep)

    # Adds the cookie into current browser context
    
    try:
        pdTemp = pd.read_html(str(table))[0]
        #if(not pd.notna(pdTemp.loc[0, "Course No."])):
            #continue
        #else:
        return pdTemp
    except:
        print("error in " + dep)
        
    
#--------main-----------------
if __name__ == "__main__":
    s = requests.Session()
    s.get('https://termmasterschedule.drexel.edu/webtms_du/')
    print(s.cookies.get_dict())
    soup = BeautifulSoup(s.get('https://termmasterschedule.drexel.edu/webtms_du/').text, 'html.parser')
    listQ = traverseQuater(soup)
    print(listQ)
    listOfDep = []
    for dep in listQ:
        try:
            listOfDep.append(traverseDeparement(dep,s))
        except:
            print(dep)
            continue
    print(listOfDep)
    listOfCourseTables = []
    print(s.cookies.get_dict())
    for table in listOfDep:
        for dep in table:
            print(dep)
            print(get_aval(dep, s))
            #listOfCourseTables.append(get_aval(dep,s))
            
    print(s.cookies.get_dict())
    #q1 = s.get(listQ[0]).content
    #soup_Q1 = BeautifulSoup(q1, 'html.parser')
    #print(soup_Q1.prettify())
    print(listOfCourseTables)

















#----------------------------------------------------------------------------------------------------------------------------old code

        


#headers = {'User-Agent': 'Mozilla/5.0'}
#print(traverseQuater())
#print(traverseDeparement(traverseQuater()[0])[0])
#print(get_aval(traverseDeparement(traverseQuater()[0])[0]))
#print(requests.get(traverseDeparement(traverseQuater()[0])[0]).url)
#print(requests("https://termmasterschedule.drexel.edu/webtms_du/courseList/ANIM", headers=headers))
#print(BeautifulSoup(requests.get("https://termmasterschedule.drexel.edu/webtms_du/courseList/ANIM").text, 'html.parser').prettify())