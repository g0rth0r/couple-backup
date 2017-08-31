#!python3
#Couple Moments Backup Tool
#This tools basically scrubs the "Moments" stored when using the Couple App.
#Lack of support and updates from Couple made me believe that the app is heading
#toward deprecation. I wanted to keep a backup of my 1000+ pictures before that 
#happens

import requests
import json
import os
import shutil
import getpass

#set the maximum pictures to request per query. Cople defaults at 30.
max_limit = 30
juliet_ver = '1.70'
moment_dir = 'moments'

#couple object
class Couple:
    
    #initiate vars to be filled
    def __init__(self):
        
        userID = ''
        authToken = ''
        sessionCookie = ''
        otherID = ''
        userUuid = ''
        pairUuid = ''
        authd = False
        
    
    #open a Couple Session, return the AuthToken Needed.
    def auth(self,user,pwd):
        
        #prepare the form data    
        form = {'userID':user,'secretKey':pwd,'set_cookie':'true'}
           
        #prepare the header
        h = {'x-juliet-ver':'1.70'}
           
        #AUTH URL
        purl = 'https://api-ssl.tenthbit.com/authenticate'
        #purl = 'https://app.couple.me/0/p/authenticate'
        
        #post the data
        p = requests.post(purl, data=form, headers=h)
        
        if p.status_code == 200:
            
            auth = p.json()
            cookie = p.headers['Set-Cookie']
            
            #debuggin only!!!
            with open('cookie.txt', 'w') as f:
                f.write(cookie)
            
            #debuggin only!!!
            json.dump(auth, open("auth.txt",'w'))
            #
            
            auth = json.load(open("auth.txt"))
            
            self.userID = auth['user']['userID']
            #AuthToken doesn't seem to be in the JSON when set_cookie = true
            #self.authToken = auth['authenticationToken']
            self.sessionCookie = p.headers['Set-Cookie']
            self.otherID = auth['user']['other']['userID']
            self.userUuid = auth['user']['uuid']
            self.pairUuid = auth['user']['other']['uuid']
            self.authd = True            
            
            print("[*] Logged-in as {}".format(self.userID))
            
            
        else:
            
            print('[!!!] Problem Authenticating')      
            
    
    def dummy_auth(self):
        
        with open('cookie.txt', 'r') as f:
            self.sessionCookie = f.read()        
        
        auth = json.load(open("auth.txt"))
        
        self.userID = auth['user']['userID']
        self.otherID = auth['user']['other']['userID']
        self.userUuid = auth['user']['uuid']
        self.pairUuid = auth['user']['other']['uuid']
        self.authd = True
        
        print("[*] Logged-in as {}".format(self.userID))
        
    #Retreive the list of pictures to download. A Session need to be opened.
    def get_moments(self,limit,itemid):
        
        #check if savepath exists, if not, create it
        if not os.path.exists(moment_dir):
            os.makedirs(moment_dir)        
        
        url = "https://app.couple.me/30/p/timeline/moments?limit={}&itemID={}&order=desc".format(limit,itemid)
                
        h = {'x-juliet-ver':'1.70','Cookie':self.sessionCookie}

        r = requests.get(url,headers=h)
        
        if r.status_code == 200:
            
            return r.json()        
        
        else:
            print("[!!!] Failed to retreive the picture listing.")
            print("[!!!] Error Code: {}".format(r.status_code))
    
    
    #initiate moments downlaod
    def download_moments(self,limit):
        
        #blank item id for the first call
        itemid = ''
        
        #by default hasmore is true at the begining
        hasmore = True
        
        #MAIN DOWNLOAD LOOP
        while hasmore:
            
            #request the json for the current ID
            pictures = self.get_moments(limit,itemid)
            
            #redefine hasmore to see if there are other pics
            hasmore = pictures['result']['more']
                
            #itterate through the pictures
            for moment in pictures['result']['timeline']:
                print('[*] Downloading... {}'.format(moment['file']))
                
                #download and look if the file was downlaoded proprely
                if download(moment['file'],moment['itemID'],moment['timeStamp']):
                    
                    #assign new id for successful dl
                    itemid = moment['itemID']
                else:
                    print('[*] Will reatempt to download picture {}'.format(moment['itemID']))
                    
                   
#
#Methods outside of couple class
#


#download url then return True or False depending on the result
def download(url,pid,time):

    #check if file was already downloaded
    if os.path.exists('{}/{}_{}.jpg'.format(moment_dir,time,pid)):
        print('[*] Image already exists. Skipping.')
        return True
    
    #download and stream to dir
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open('{}/{}_{}.jpg'.format(moment_dir,time,pid), 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f) 
        print('[*] Done!')
        return True
    else:
        print('[!!] Error retreiving image. Skipping')
        return False
    
#create a new Couple object
couple = Couple()

user = input('Please enter your username/email address: ')
pwd = getpass.getpass(prompt='Enter your password: ')

#AUTH
couple.auth(user,pwd)

#DEBUG AUTH (uses a txt file instead of actual auth)
#couple.dummy_auth()

couple.download_moments(30)

#pic = readjson('pics.txt')

    
