from base64 import encode
from bs4 import BeautifulSoup
import requests

html_text = requests.get('http://bocznica.eu/files/archiwum/aktualny.html')
html_text.encoding = 'UTF-8'
html_text = html_text.text
soup = BeautifulSoup(html_text, 'lxml')
train = soup.find_all('table', class_='table0')
for t in train:
    #print(t)
    cell = t.find_all('td')
    attributeList = cell[1].text.replace(' ','').replace('\n\n','\n')
    attributeList = attributeList.rsplit("\n")
    attributeList.pop(0)
    attributeList.pop()
    attributes = cell[2].text.replace('    ','').replace('\n\n','\n')
    attributes = attributes.rsplit("\n")
    attributes.pop(0)
    attributes.pop()
    infosRAW = cell[3]

    print (attributeList)
    print ('--')
    print (attributes)
    print ('--')
    print (infosRAW)
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