#importing libraries
import json, sys, subprocess, base64
from flatten_json import flatten
from datetime import date
import psycopg2

#storing the local SQS url in a variable
queue_url = 'http://localhost:4566/000000000000/login-queue'

#Receiving the messages from the SQS queue and storing the messages in the variable "output" using
#the subprocess library which lets you collect data from the output of the terminal
sp = subprocess.Popen(["awslocal", "sqs", "receive-message", "--queue-url", queue_url], stdout=subprocess.PIPE)
output, error= sp.communicate()

#convert to utf-8
output= output.decode("utf-8")

#Parse the JSON String with json.loads and convert it to a python dictionary
#Then flatten the data using the flatten_json library
data=json.loads(output)
data=flatten(data)

#connecting to the postgres database
try:
    connection = psycopg2.connect(
                host="localhost",
                dbname="postgres",
                user="postgres",
                password="postgres",
                port=5432)
    cursor = connection.cursor()
except Exception as error:
    #if there are any errors, print them out and immediately exit
    print(error)
    sys.exit()

#create a dictionary with the different fields of the database table
mydict = {"user_id": "", 
        "device_type": "", 
        "masked_ip": "", 
        "masked_device_id": "", 
        "locale": "", 
        "app_version": ""}

#store today's date for the date field
create_date=date.today()

#store the fields we must mask here
fieldstomask= ['device_id', 'ip']

#loop through the data
for content in data:
    #go to the contents of the body of the data, not the MD5OfBody (which is another field that also has the word "Body")
    if(content.find('Body')!=-1 and content.find('MD5OfBody')==-1):
        #Parse the JSON string and store it in the python dictionary "body"
        body=json.loads(data[content])
        #loop through the different fields of the body
        for field in body:
            #for the fields that we must mask, convert the PII to a base64-encoded String
            if field in fieldstomask:
                #masking the data by converting to bytes first and then encoding with the base64 module
                bytes=base64.b64encode(body[field].encode("ascii"))
                body[field]=bytes.decode("ascii")

                #The below code is how you would mask it by hashing the values, but this makes the PII irreversible:
                #body[field]=hashlib.sha256(body[field].encode()).hexdigest()

            #for the rest of the fields, add the appropriate value to associate with the dictionary key
            if(field=="user_id"):
                mydict["user_id"]=body[field]
            elif(field=="device_type"):
                mydict["device_type"]=body[field]
            elif(field=="ip"):
                mydict["masked_ip"]=body[field]
            elif(field=="device_id"):
                mydict["masked_device_id"]=body[field]
            elif(field=="locale"):
                mydict["locale"]=body[field]
            elif(field=="app_version"):
                # for the "version" field it needs to be an integer in the postgres database, and 
                # a number like 2.3.0 cannot be converted to an integer in any way, so I remove the decimals
                # to convert to an integer. Otherwise the database cannot store the String "2.3.0"
                body[field]= body[field].replace('.', '')
                mydict["app_version"]=int(body[field])


        #Now we can write to the postgres database
        #Using the values in the dictionary as all the values have been appropriately initialized
        cursor.execute("""INSERT INTO user_logins (user_id, device_type, masked_ip, 
        masked_device_id, locale, app_version, create_date) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (mydict["user_id"], mydict["device_type"], mydict["masked_ip"], mydict["masked_device_id"], mydict["locale"], mydict["app_version"], create_date))

        """
        One way that I would continue fleshing this project out is for a verion number
        like 2.3.0, I would need to find a better way to convert it to an integer and store it in the 
        postgres database
        """ 

        #commit the changes to the postgres database
        connection.commit()

        #clear the dictionary
        mydict= mydict.fromkeys(mydict, "")

        
#close the connections
cursor.close()
connection.close()


