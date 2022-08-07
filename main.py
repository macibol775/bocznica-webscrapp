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
    carNo = 0
    carType = 0
    infosA = cell.find_all('p', class_ = "klasaA")
    infosAB = cell.find_all('p', class_ = "klasaAB")
    infosB = cell.find_all('p', class_ = "klasaB")
    if len(infosA) == 2:
        carNo = infosA[0].text
        carType = infosA[1].text
    if len(infosAB) == 2:
        carNo = infosAB[0].text
        carType = infosAB[1].text
    elif len(infosB) == 2:
        carNo = infosB[0].text
        carType = infosB[1].text

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
    return Car(carNo, None, carType, from_, to, ann)

def deleteDuplicates(list_):
    list_ = list(dict.fromkeys(list_))
    return list_
class Car:
    def __init__(self, no, attributes, type, relFrom, relTo, annotations):
        self.no = no
        self.attributes = attributes
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
    #finding attribute names
    attributeList = cell[1].text.replace(' ','').replace('\n\n','\n')
    attributeList = attributeList.rsplit("\n")
    attributeList.pop(0)
    attributeList.pop()
    #finding attribute values
    attributes = cell[2].text.replace('    ','').replace('\n\n','\n')
    attributes = attributes.rsplit("\n")
    attributes = list(filter(None, attributes))
    #train no, name, code, category
    infosRAW = cell[3]  
    attrList = {}
    for a in range (len(attributeList)):
        attrList[attributeList[a]] = attributes[a]
        if (attributeList[a] == 'Obiegi:'):
            attrList['Obiegi:'] = re.split(' ; |, | - |/', attributes[a])
            for ob in range (len(attrList['Obiegi:'])):
                if len(attrList['Obiegi:'][ob]) > 10:
                    attrList['Obiegi:'][ob] = ''
            attrList['Obiegi:'] = deleteDuplicates(attrList[attributeList[a]])#delete duplicates
            attrList['Obiegi:'] = list(filter(None, attrList[attributeList[a]])) #delete empty
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
    cars_count = 0
    for a in range (4, len(cell) - 1):
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

            elif (isMultipleUnit(locos[0].name) == 0):
                cars.append(create_car(cell[a]))
            else:
                cars_count += 1
    if isMultipleUnit(locos[0].name):
        times = cars_count / isMultipleUnit(locos[0].name)
        if not times == 1:
            locos[0].name = str(times) + 'x ' + str(locos[0].name)
    for l in locos:
        print (l)
        allLocos.append(l.name)
    for c in cars:
        print (str(c.no))
    print('-------------')
    for p in attrList['Obiegi:']:
        allCirculations.append(p)
print ('================================================================')
print ('Obiegi:')
allCirculations = deleteDuplicates(allCirculations)
allLocos = deleteDuplicates(allLocos)
for c in allCirculations:
    print (c)
print ('Lokomotywy i EZT:')
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