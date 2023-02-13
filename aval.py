import requests, html5lib
from bs4 import BeautifulSoup
import pandas as pd

s = requests.Session()
def traverseQuater():
    lsitOfQuaters = []
    listUrlQ = []
    quaters = requests.get('https://termmasterschedule.drexel.edu/webtms_du/').text
    soup = BeautifulSoup(quaters, 'html.parser')
    terms = soup.find_all("div", {"class": "term"})
    for term in terms:
        if len(lsitOfQuaters) == 4:
            break
        quater = term.find('a')
        lsitOfQuaters.append(quater)
    for quater in lsitOfQuaters:
        listUrlQ.append("https://termmasterschedule.drexel.edu" + quater.get('href'))
    return listUrlQ
        
def traverseDeparement(quarter):
    depList = []
    soup = BeautifulSoup(requests.get(quarter).text, 'html.parser')
    depPannel = soup.find("table", {"class": "collegePanel"})
    departments = depPannel.find_all("class" == "odd")
    departments.append(depPannel.find_all("class" == "even"))
    for department in departments:
        
        try:
            depList.append("https://termmasterschedule.drexel.edu"+department.find('a').get('href').split(';')[0])
        except:
            continue
    return depList
def get_aval(dep):
    print(dep)
    soup = BeautifulSoup(requests.get(dep).text, 'html.parser')
    print(soup.prettify())
    table = soup.find_all("table", id != None and id != "breadcrumbs", class_ = None, _class = "collegePanel")
    #print(table)
    return pd.read_html(str(table))[0]

headers = {'User-Agent': 'Mozilla/5.0'}
print(traverseQuater())
print(traverseDeparement(traverseQuater()[0])[0])
#print(get_aval(traverseDeparement(traverseQuater()[0])[0]))
print(requests.get(traverseDeparement(traverseQuater()[0])[0]).url)
print(requests.head("https://termmasterschedule.drexel.edu/webtms_du/courseList/ANIM", headers=headers))
#print(BeautifulSoup(requests.get("https://termmasterschedule.drexel.edu/webtms_du/courseList/ANIM").text, 'html.parser').prettify())