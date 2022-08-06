from base64 import encode
from bs4 import BeautifulSoup
import requests
import re

class Loco:
    def __init__(self, name, relFrom, relTo, annotations):
        self.name = name
        self.relFrom = relFrom
        self.relTo = relTo
        self.annotations = annotations
    def __str__(self):
        return str(self.name) + ' (' + str(self.relFrom) + ' - ' + str(self.relTo) + ') ' + str(self.annotations)

def create_loco(cell):
    lok = cell.find('p', class_ = "Lok").text
    from_ = cell.find('p', class_ = "relOd")
    if not (from_ == None):
        from_ = from_.text.replace(' - ', '')
    
    to = cell.find('p', class_ = "relDo")
    if not (to == None):
        to = to.text.replace(' - ', '')
    ann = cell.find('div', class_ = "wagUwagi")
    if not (ann == None):
        ann = ann.text.replace('\n', '').replace('  ', '').replace(';', '')
        ann = ann.rsplit('-')
        ann = list(filter(None, ann)) #delete empty
    return Loco(lok, from_, to, ann)

def isMultipleUnit(name):
    if name == 'SN84':
        return 3
    elif name == 'ED160' or name == 'ED161':
        return 8
    elif name == 'ED250':
        return 7
    elif name == 'ED74':
        return 4
    elif name == 'HRCS2':  
        return 9
    else:
         return 0

def create_car(cell):
    return 0

def deleteDuplicates(list_):
    list_ = list(dict.fromkeys(list_))
    return list_
class Car:
    def __init__(self, no, class_, type, relFrom, relTo, annotations):
        self.no = no
        self.class_ = class_
        self.type = type
        self.relFrom = relFrom
        self.relTo = relTo
        self.annotations = annotations

#downloading website
html_text = requests.get('http://137.74.97.52/files/archiwum/aktualny.html')
html_text.encoding = 'UTF-8'
html_text = html_text.text
soup = BeautifulSoup(html_text, 'lxml')
#selecting trains
train = soup.find_all('table', class_='table0')

allLocos = [] #DEBUG ONLY
allCirculations = [] #DEBUG ONLY

for t in train:
    #dividing train into website parts
    cell = t.find_all('td')
    #finding attributes
    attributeList = cell[1].text.replace(' ','').replace('\n\n','\n')
    attributeList = attributeList.rsplit("\n")
    attributeList.pop(0)
    attributeList.pop()
    attributes = cell[2].text.replace('    ','').replace('\n\n','\n')
    attributes = attributes.rsplit("\n")
    attributes = list(filter(None, attributes))
    infosRAW = cell[3]
    attrList = {}
    for a in range (len(attributeList)):
        attrList[attributeList[a]] = attributes[a]
        if (attributeList[a] == 'Obiegi:'):
            attrList[attributeList[a]] = re.split(' ; |, | - |/', attributes[a])
            attrList[attributeList[a]] = deleteDuplicates(attrList[attributeList[a]])#delete duplicates
            attrList[attributeList[a]] = list(filter(None, attrList[attributeList[a]])) #delete empty
    category = infosRAW.b.extract().text    #IC/EIC/EIP/TLK
    name = infosRAW.b.extract().text
    infosRAW = infosRAW.text.replace('  ','').replace('\n','').rsplit(' ')
    code = infosRAW[1]  # unfriendly letters
    no = infosRAW[2]    # no of train
    #friendlyName for printing
    friendlyName = category + ' ' + name + ' (' + no + ')'
    print (attrList)
    print ('--')
    print (friendlyName)
    print ('----')
    locos = [] #array of locomotives
    cars = []  #array of cars
    for a in range (4, len(cell)):
        cars_count = 0
        if not (cell[a].get('class')):  #ommit loco separator
            lok = cell[a].find('p', class_ = "Lok")
            if (lok):   #if it's a loco
                if (len(locos) <= 0): #no locos in the list  
                    locos.append(create_loco(cell[a]))
                else:
                    if (locos[len(locos) - 1].name == lok): #previous loco is the same
                        locos[len(locos) - 1].relTo = cell.find('p', class_ = "relDo").text.replace(' - ', '')
                    else:   #loco is different
                        locos.append(create_loco(cell[a]))
                for l in locos:
                    #print (l)
                    allLocos.append(l.name)
            elif (isMultipleUnit(locos[0].name) == 0):
                cars.append(create_car(cell[a]))
            else:
                cars_count += 1
    if isMultipleUnit(locos[0].name):
        times = isMultipleUnit(locos[0].name) / cars_count
        if not times == 1:
            locos[0].name = str(times) + 'x ' + str(locos[0].name)
    print('-------------')
    for p in attrList['Obiegi:']:
        allCirculations.append(p)
print ('================================================================')
allCirculations = deleteDuplicates(allCirculations)
allLocos = deleteDuplicates(allLocos)
for c in allCirculations:
    print (c)
print ('================================================================')
for l in allLocos:
    print (l)

# with open('aktualny.html', mode='r', encoding='utf-8') as webpage:
#    content = webpage.read()
#    soup = BeautifulSoup (content, 'lxml')
#    train_cells = soup.find_all('table')
#    for tc in train_cells:
#        test = tc.find_all('center')
#        for test_ in test:
#            print (test_.text)
#            print ('-')
#        loco_type = tc.find_all('p', class_='Lok')
#
#        for loco in loco_type:
#            print (loco.text)
#        print('==========================')