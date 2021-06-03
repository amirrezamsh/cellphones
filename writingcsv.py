from bs4 import BeautifulSoup as bs
import urllib.request, urllib.parse, urllib.error
import re
import time
import datetime as dt
import numpy as np

def parsecamera(spec,main=True) :
    txt=spec.find_all('tr')[0].get_text().strip()
    wide,telephoto=str(0),str(0)
    if 'wide' in txt : wide=str(1)
    if 'telephoto' in txt : telephoto=str(1)

    mpx=re.findall('[0-9.]+[, ]+MP',txt)
    if (' or ' in txt) or ('Q Stylus' in txt) : mpx=list(max(mpx))
    cams=''
    for i in range(len(mpx)) :
        if i==len(mpx)-1 :
            cams+=mpx[i]
        else : cams+=mpx[i]+'+'
    cams=cams.replace('MP','').replace(' ','')
    if main==True :
        return (cams,wide,telephoto)
    else :
        return cams

with open('links.txt','r') as handle :
    links=handle.readlines()
    if len(links)<1 :
        print('nothing found in links.txt')
        exit()
sit=int(input('press 0 if it is the first time: '))
if sit==0 :
    h=open('cellphones.csv','w')
    h.write('brand,model,launch,weight,display type,display size,ppi,cpu,gpu,main camera,wide,telephoto,selfie,battery\n')
else :
    with open('cellphones.csv','r') as r :
        models=[line.split(',')[1] for line in r]
    h=open('cellphones.csv','a')
c=1
for link in links :
    if c%5==0 :
        print('pausing the prcess for one minute...')
        time.sleep(60)
    for item in re.finditer('com\/(?P<brand>[a-z]*)_(?P<model>[a-z0-9_+]*)',link) :
        brand=item.groupdict()['brand'].capitalize()
        model=item.groupdict()['model'].replace('_',' ')
        if sit!=0 :
            if model in models :
                print('found in file',model)
                continue
        try :
            html=urllib.request.urlopen(link).read()
        except urllib.error.HTTPError :
            print('Too many requests, Closing the program')
            h.close()
            exit()
        soup=bs(html,'html.parser')
        specs=soup.select('div#specs-list table')

        launch=specs[1].find_all('td',class_='nfo')[0].get_text().strip()
        launch=re.findall('[0-9]+, [\w]+',launch)[0]
        launch=str(dt.datetime.strptime(launch,'%Y, %B'))
        launch=re.findall('[\d]+\-[\d]+',launch)[0]

        weight=specs[2].find_all('tr')[1].get_text()
        weight=re.findall('[0-9]+',weight)[0].strip()

        dtype=specs[3].find_all('tr')[0].get_text().strip().split('\n')[-1]
        try :
            dtype=dtype.split(',')[0]
        except : pass

        dsize=specs[3].find_all('tr')[1].get_text()
        dsize=re.findall('([0-9.]+) inches',dsize)[0]

        ppi=specs[3].find_all('tr')[2].get_text().strip().split('\n')[-1]
        ppi=re.findall('\(~([\d]+)',ppi)[0]

        cpu=specs[4].find_all('tr')[2].get_text().strip().split('\n')[-1]
        #print(cpu)
        try :
            cpu=cpu.split(' - ')[0].strip()
        except : pass

        gpu=specs[4].find_all('tr')[3].get_text().strip().split('\n')[-1]
        try :
            gpu=gpu.split(' - ')[0].strip()
        except : pass
        #print(gpu)

        (mcam,wide,telephoto)=parsecamera(specs[6])

        selfie=parsecamera(specs[7],main=False)

        battery=specs[11].find_all('tr')[0].get_text().strip().split('\n')[-1]
        battery=re.findall('([\d]+) mAh',battery)[0]

        ans=[brand,model,launch,weight,dtype,dsize,ppi,cpu,gpu,mcam,wide,telephoto,selfie,battery]
        anstext=','.join(ans)

        h.write(anstext+'\n')

        pause=np.random.randint(9,18)
        print(c,brand,model,'pause:',pause,sep=',',end='\n')
        time.sleep(pause)
        c+=1
