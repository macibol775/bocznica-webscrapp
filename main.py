from base64 import encode
from bs4 import BeautifulSoup
import requests

#downloading website
html_text = requests.get('http://137.74.97.52/files/archiwum/aktualny.html')
html_text.encoding = 'UTF-8'
html_text = html_text.text
soup = BeautifulSoup(html_text, 'lxml')
#selecting trains
train = soup.find_all('table', class_='table0')
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
    attributes.pop(0)
    attributes.pop()
    infosRAW = cell[3]
    attrList = {}
    for a in range (len(attributeList)):
        attrList[attributeList[a]] = attributes[a]
    category = infosRAW.b.extract().text
    name = infosRAW.b.extract().text
    infosRAW = infosRAW.text.replace('  ','').replace('\n','').rsplit(' ')
    code = infosRAW[1]
    no = infosRAW[2]
    #friendlyName for printing
    friendlyName = category + ' ' + name + ' (' + no + ')'
    print (attrList)
    print ('--')
    print (friendlyName)
    print ('----')
    for a in range (4, len(cell)):
        print(cell[a])
        print ('--')
    print('-------------')



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