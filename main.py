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
        string = str(self.name)
        if not self.relTo == None:
            string += ' (' + str(self.relFrom) + ' - ' + str(self.relTo) + ')'
        if not self.annotations == None:
            string += ' ' + str(self.annotations)
        return string

def create_loco(cell):
    lok = cell.find('p', class_ = "Lok").text
    from_ = findFrom(cell)
    to = findTo(cell)
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

def findFrom(cell):
    from_ = cell.find('p', class_ = "relOd")
    if not (from_ == None):
        from_ = from_.text.replace(' - ', '').replace(' -', '').replace(')', '')
    return from_

def findTo(cell):
    to = cell.find('p', class_ = "relDo")
    if not (to == None):
        to = to.text.replace(' - ', '').replace('- ', '').replace(')', '')
    return to

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
    attributes = []
    from_ = findFrom(cell)
    to = findTo(cell)
    ann = cell.find('div', class_ = "wagUwagi")
    if not (ann == None):
        ann = ann.text.replace('\n', '').replace('  ', '').replace(';', '')
        ann = ann.rsplit('-')
        ann = list(filter(None, ann)) #delete empty
    pics = cell.find_all('img')
    for p in pics:
        tag = p.get('title')
        if not tag == None:
            attributes.append(tag)
    return Car(carNo, attributes, carType, from_, to, ann)

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

    def __str__(self):
        string = str(self.no) + ': ' + str(self.type)
        if not self.relTo == None:
            string += ' (' + str(self.relFrom) + ' - ' + str(self.relTo) + ')'
        if not self.attributes == None:
            string += ' ' + str(self.attributes)
        if not self.annotations == None:
            string += ' ' + str(self.annotations)
        return string

class Train:
    def __init__(self, number, category, route, name, runs, annotations, applies, locos, cars, circulations):
        self.number = number
        self.category = category
        self.route = route
        self.name = name
        self.runs = runs
        self.annotations = annotations
        self.applies = applies
        self.locos = locos
        self.cars = cars
        self.circulations = circulations

    def __str__(self):
        string = str(self.category) + ' ' + str(self.number)
        if (len(self.name) > 0):
            string += ' (' + self.name + ')'
        string += '\nTrasa: ' + self.route
        if not self.runs == None:
            string += '\nKursuje: ' + self.runs
        if not self.applies == None:
            string += '\nObowiązuje: ' + self.applies
        if not self.circulations == None:
            string += '\nObiegi: ' + str(self.circulations)
        for l in self.locos:
            string += '\n' + str(l)
        for c in self.cars:
            string += '\n' + str(c)
        if not self.annotations == None:
            string += '\nUwagi: ' + self.annotations
        return string

#downloading website
trains_file = open ("trains.txt", "w")
locos_file = open ("locos.txt", "w")
circul_file = open ("circulations.txt", "w")
html_text = requests.get('http://137.74.97.52/files/archiwum/aktualny.html')
html_text.encoding = 'UTF-8'
html_text = html_text.text
soup = BeautifulSoup(html_text, 'lxml')
#selecting trains
train = soup.find_all('table', class_='table0')
train1 = soup.find_all('table', class_='table1')
train += train1
allLocos = [] #DEBUG ONLY
allCirculations = [] #DEBUG ONLY

trains = []

for t in train:
    #dividing train into website partsclea
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
                    if (locos[len(locos) - 1].name == lok.text): #previous loco is the same
                        locos[len(locos) - 1].relTo = cell[a].find('p', class_ = "relDo").text.replace(' - ', '')
                    else:   #loco is different
                        locos.append(create_loco(cell[a]))

            elif (isMultipleUnit(locos[0].name) == 0):
                cars.append(create_car(cell[a]))
            else:
                cars_count += 1
    if isMultipleUnit(locos[0].name):
        times = cars_count / isMultipleUnit(locos[0].name)
        for x in range(1, int(times)):
            locos.append(Loco (locos[0].name, locos[0].relFrom, locos[0].relTo, locos[0].annotations))
        c = 6
        l = 0
        while c < (len(cell) - 6):
            locos[l].relFrom = findFrom(cell[c])
            locos[l].relTo = findTo(cell[c])
            c += (isMultipleUnit(locos[0].name) + 1)
            l += 1
    for l in locos:
        allLocos.append(l.name)
    for p in attrList['Obiegi:']:
        allCirculations.append(p)
    trains.append(Train(no, category, attrList.get('Relacja:'), name, attrList.get('Kursuje:'), attrList.get('Info:'), attrList.get('Obowiązuje:'), locos, cars, attrList.get('Obiegi:')))
#file.write ('Obiegi:\n')
for t in trains:
    trains_file.write(str(t))
    trains_file.write('\n=======\n')
allCirculations = deleteDuplicates(allCirculations)
allLocos = deleteDuplicates(allLocos)
allCirculations.sort()
allLocos.sort()
for c in allCirculations:
    circul_file.write(c)
    circul_file.write('\n=======\n')
    for t in trains:
        if t.circulations.count(c) > 0:
            circul_file.write (str(t))
            circul_file.write('\n=======\n')
    circul_file.write('----------------------------------\n')
#file.write ('Lokomotywy i EZT:')
for l in allLocos:
    locos_file.write(l)
    locos_file.write('\n=======\n')
    for t in trains:
        for lo in t.locos:
            if  lo.name == l:
                locos_file.write (str(t))
                locos_file.write('\n=======\n')
    locos_file.write('----------------------------------\n')

trains_file.close()
locos_file.close()
circul_file.close()


# with open('aktualny.html', mode='r', encoding='utf-8') as webpage:
#    content = webpage.read()
#    soup = BeautifulSoup (content, 'lxml')
