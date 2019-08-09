import bs4, requests as requests, smtplib
import re

# convert extract h3 tag to string
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

def fetch_special():
    getPage = requests.get('https://ramen.ie/whats-the-6before6/', verify = False)
       
    '''    
    # if you are sending too many requests to the server, try wait some time and try again
    page = ''
    while page == '':
        try:
            getPage = requests.get('https://ramen.ie/whats-the-6before6/')
            break
        except:
            print("Connection refused by the server..")
            print("Let me sleep for 5 seconds")
            print("ZZzzzz...")
            time.sleep(5)
            print("Was a nice sleep, now let me continue...")
            continue
    '''
    
    #To validate if all the download happened without any issues, the raise_for_status() function can be used:
    getPage.raise_for_status() 
    
    # parses and returns just the text    
    text = bs4.BeautifulSoup(getPage.text, 'html.parser')
    
    ### Updated HTML Parsing Code ###
    # I only edited this code because the format of the target page seems to have changed during the gig.
    text = text.find('h3').findParent()
    text = bs4ToText(text)
    text = text[11]
    text = text.lower()
    return cleanhtml(text)

# I put connection info into a separate function for the following reasons:
# 1. If we ever need multiple twlilio connections, it makes it easy to keep track of the different sets of similiar information because each info set is contained in a dictionary
# 2. The TWILIO_MESSAGE_ENDPOINT is actually dependent on the TWILIO_SID, so we want to ensure those declarations are never separated.
def twilio_connection_info():

    TWILIO_SID = "AC30079d29bc59eae298b#########"
    TWILIO_AUTHTOKEN = "3c22142f3eb3456c57#########"
    TWILIO_MESSAGE_ENDPOINT = "https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json".format(TWILIO_SID=TWILIO_SID)
    TWILIO_NUMBER = "whatsapp:+1415523#####"

    return {
        'SID' : TWILIO_SID,
        'AUTHTOKEN' : TWILIO_AUTHTOKEN,
        'MESSAGE_ENDPOINT' : TWILIO_MESSAGE_ENDPOINT,
        'NUMBER' : TWILIO_NUMBER
    }
    
def email_connection_info():
    return {
        'email' : 'sixbeforesix@gmail.com',
        'password' : '##########'
    }

# The transmitter object is designed to to handle all communication setup between other services and our app.
# The goal of this object is to send an email / message without having to do any configuration at the time-of-sending.
class Transmitter:
    
    def __init__(self, twilio_connection, email_connection):
        self._TWILIO_SID = twilio_connection['SID']
        self._TWILIO_AUTHTOKEN = twilio_connection['AUTHTOKEN']
        self._TWILIO_MESSAGE_ENDPOINT = twilio_connection['MESSAGE_ENDPOINT']
        self._TWILIO_NUMBER = twilio_connection['NUMBER']
    
        self._sender_email_address = email_connection['email']
        self._sender_email_password = email_connection['password']
    
    # The send_whatsapp_message and send_email functions are designed to be modular and take a minimum amount of information.
    # This will allow you to reuse this Transmitter object across applications without needing to change a lot of information.    
    def send_whatsapp_message(self, recipients, message):
        responses = []
        for recipient in recipients:
            message_data = {
                "To": recipient,
                "From": self._TWILIO_NUMBER,
                "Body": message,
            }
            
            response = requests.post(
                self._TWILIO_MESSAGE_ENDPOINT, 
                data=message_data, 
                auth=(self._TWILIO_SID, self._TWILIO_AUTHTOKEN))
            responses.append(response.json())
        return responses
    
    def send_email(self, recipients, message):
        conn = smtplib.SMTP('smtp.gmail.com', 587) # smtp address and port
        conn.ehlo() # call this to start the connection
        conn.starttls() # starts tls encryption. When we send our password it will be encrypted.
        conn.login(
            self._sender_email_address, 
            self._sender_email_password) #https://www.google.com/settings/security/lesssecureapps may need to allow 'less secure apps' to allow login
        for recipient in recipients:
            conn.sendmail(
                self._sender_email_address,
                recipient, 
                message)
        conn.quit()

# This function generates the text to send in email / phone messages.
def generate_special_messages(daily_special):
    messages = {
        'pad thai' : {
            'phone' : 'Pad Thai',
            'email' : 'Pad Thai'
        },
        'fire cracker' : {
            'phone' : 'Fire Cracker',
            'email' : 'Fire Cracker'
        },
        'firecracker' : { #This is a duplicate entry, but it allows you to process both 'fire cracker' and 'firecracker' names.
            'phone' : 'Fire Cracker',
            'email' : 'Fire Cracker'
        },
        'tikka' : {
            'phone' : 'Tikka Masala',
            'email' : 'Tikka Masala' 
        },
        'katsu curry' : {
            'phone' : 'Katsu Curry',
            'email' : 'Katsu Curry'
        },
        'khao pad' : {
            'phone' : 'Khao Pad',
            'email' : 'Khao Pad'
        },
        'thai green curry' : {  
            'phone' : 'Thai Green Curry',
            'email' : 'Thai Green Curry'
        },
        'red curry' : {  
            'phone' : 'Red Curry',
            'email' : 'Red Curry'
        },
        'massaman curry' : { 
            'phone' : 'Massaman Curry',
            'email' : 'Massaman Curry'
        }
    }
    
    if daily_special in messages.keys():
        return {
            'phone' : "Your {0} code is {1}".format('Ramen Secret 6b46', messages[daily_special]['phone']),
            'email' : 'Subject:' + messages[daily_special]['email'] + ' Alert!\n\nAttention!\n\nThis is an automated mail. Your favourite food is available today!\n\nBon appetit!:\nFood Notifier v1.0\n\nTo unsubscribe from this notification or phone notifications, please request removal from the mailing list by responding to this e-mail.'
        }

def main():
    daily_special = fetch_special()
    special_messages = generate_special_messages(daily_special)
    if not special_messages:
        return
    
    transmitter = Transmitter(
        twilio_connection_info(), 
        email_connection_info())
        
    recipient_numbers = ["whatsapp:+353##########"]
    recipient_emails = ['ob#######@######.com']
    
    print(special_messages['phone'])
    print(special_messages['email'])
    
    
    transmitter.send_whatsapp_message(
         recipient_numbers,
         special_messages['phone'])
    
    transmitter.send_email(
         recipient_emails,
         special_messages['email'])
  
if __name__ == '__main__':
    main()
