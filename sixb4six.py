#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 11:01:30 2019

@author: Ciaran
"""

import bs4, requests, smtplib
import re

# convert extract h2 tag to string
def bs4ToText(bs4):
    text = []
    for x in bs4:
        text.append(str(x))
    return(text)

# clean text of html tags
def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

# Check and see is my favourite on the menu
def onTheMenu(sixBeforeSix,the_one = 'Black Bean'):
    # find is your choice on the menu today
    available = False
    
    # set everything to lower case
    if sixBeforeSix.lower() == the_one.lower():
        available = True
        
    return available
        
def main():
    getPage = requests.get('https://ramen.ie/whats-the-6before6/')
    
    #To validate if all the download happened without any issues, the raise_for_status() function can be used:
    getPage.raise_for_status() 
    
    # parses and returns just the text    
    text = bs4.BeautifulSoup(getPage.text, 'html.parser')
    
    # pulls out h2 headings, where the name of the 6b46 is listed 
    div_contents = text.find('h2').findParent()
    type(div_contents)
    
    # Convert bs4 element tag to text in preparation for cleaning
    div_contents_text = bs4ToText(div_contents)
    
    # get 6b46
    sixBeforeSix = div_contents_text[3]
    
    # remove html tags from 64b6 string
    sixBeforeSix = cleanhtml(sixBeforeSix)
    
    # is 6b46 on the menu?
    available = onTheMenu(sixBeforeSix)
    
    if available == True:
        toAddress = ['obrienciaran@hotmail.co.uk']

        
        conn = smtplib.SMTP('smtp.gmail.com', 587) # smtp address and port
        conn.ehlo() # call this to start the connection
        conn.starttls() # starts tls encryption. When we send our password it will be encrypted.
        conn.login('ciaranobrienmusic@gmail.com', 'highfield76') #https://www.google.com/settings/security/lesssecureapps may need to allow 'less secure apps' to allow login
        conn.sendmail('ciaranobrienmusic@gmail.com', toAddress, 'Subject: Pad Thai Alert!\n\nAttention!\n\nYour favourite food is available today!\n\nBon apetite!:\nFood Notifier V1.0')
        conn.quit()
        print('Sent notificaton e-mails for the following recipients:\n')
        for i in range(len(toAddress)):
            print(toAddress[i])
        print('')
    else:
        print('Your favourite food is not available today.')    

if __name__ == '__main__':
    main()


