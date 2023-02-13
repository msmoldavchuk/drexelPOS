import requests, html5lib
from bs4 import BeautifulSoup
import pandas as pd

def traverseQuater(soup):
    lsitOfQuaters = []
    listUrlQ = []
    terms = soup.find_all("div", {"class": "term"})
    for term in terms:
        if len(lsitOfQuaters) == 4:
            break
        quater = term.find('a')
        lsitOfQuaters.append(quater)
    for quater in lsitOfQuaters:
        listUrlQ.append("https://termmasterschedule.drexel.edu" + quater.get('href'))
    return listUrlQ


def traverseDeparement(quarter,session : requests.Session):
    depList = []
    soup = BeautifulSoup(s.get(quarter).text, 'html.parser')
    depPannel = soup.find("table", {"class": "collegePanel"})
    departments = depPannel.find_all("class" == "odd")
    departments.append(depPannel.find_all("class" == "even"))
    for dep in departments:
        try:
            depList.append("https://termmasterschedule.drexel.edu" + dep.find('a').get('href'))
        except:
            continue
    return depList

def get_aval(dep, session : requests.Session):
    soup = BeautifulSoup(session.get(dep).text, 'html.parser')
    table = soup.find_all("table")
    return pd.read_html(str(table))[0]
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
        listOfDep.append(traverseDeparement(dep,s))
    print(listOfDep)
    listOfCourseTables = []
    for table in listOfDep:
        for dep in table:
            listOfCourseTables.append(get_aval(dep,s))
    #q1 = s.get(listQ[0]).content
    #soup_Q1 = BeautifulSoup(q1, 'html.parser')
    #print(soup_Q1.prettify())
    print(listOfCourseTables[0])

















#----------------------------------------------------------------------------------------------------------------------------old code

        


#headers = {'User-Agent': 'Mozilla/5.0'}
#print(traverseQuater())
#print(traverseDeparement(traverseQuater()[0])[0])
#print(get_aval(traverseDeparement(traverseQuater()[0])[0]))
#print(requests.get(traverseDeparement(traverseQuater()[0])[0]).url)
#print(requests("https://termmasterschedule.drexel.edu/webtms_du/courseList/ANIM", headers=headers))
#print(BeautifulSoup(requests.get("https://termmasterschedule.drexel.edu/webtms_du/courseList/ANIM").text, 'html.parser').prettify())