**# Fetch_TakeHome**

This program reads messages from the AWS SQS Queue, and, after making modifications to the data and the messages contained in the data, the data is written to a Postgres database.

Comments are written throughout the code and explain the script in greater detail. Libraries such as json, flatten_json, base64, subprocess, and psycopg2 are used. The messages are read from the queue and written to the database in the code.

At first, I masked the PII with sha256 hashing, but this makes the PII irretrievable again once it is hashed. The code for the sha256 hashing is still in the program, and one can use this far more secure hashing while storing the PII in another private database for even more security of the PII.

**Steps for executing the program:**

1. install python 3
2. Make sure both the given docker containers are running
3. Run by executing “python3 fetch.py”


**How would you deploy this application in production?** 
You would deploy this application as AWS lambda and leverage other AWS services like AWS SQS and mysql.

**How can this application scale with a growing dataset?**
The application runs in about O(N*M) time, where N is the number of fields in the body of the message and M is the number of fields in the message itself. This would run into issues if N*M exceeded 10^6, as this would likely take more than five seconds to run and would be highly intensive. One way to help this application scale is automatically filtering out the duplicate values immediately so they don’t have to be removed later on. Another way is implementing multithreading where you read 1,000 messages at a time and load them using different threads so they can be run in parallel.

**How can PII be recovered later on?** 
Since the PII is base-64 encoded, the PII can be recovered later on through base 64 decoding, which is also an available python function.

**What are the assumptions you made?**
One assumption I made is that there are not blank or nonexistent fields in the message, and that all the fields are filled, as this is not accounted for. Another assumption made is that the message fields shown are the only message fields the message will have. Finally, the third assumption made is that base64 encoding is sufficient masking of the PII, but this may not be the case as the PII is still able to be retrieved by hackers.

**Next Steps:**
To make this production ready, I’d first need to check for blank or nonexistent inputs in the messages and put an indication on the postgres database so it is easy for data analysts to see this. One simple way would be to have a keyword like “None” indicating a field that is not applicable for the message. Another important step to make this application production-ready is utilizing sha 256 hashing or another form of very secure hashing and being able to still recover the PII by storing it in another completely private database. This way, there is no way for someone to be able to decode the PII the way that they can with base64. It would also be more optimal to automatically remove the duplicate messages from the database rather so they don’t have to be removed later on. Other steps would be creating functions that remove and modify rows from the database to make testing and manipulation much easier. Finally, for version numbers like 2.4.6 or 2.3.0, there should be a way to store the version numbers in the postgres database, or the database field should be changed to a String as the value cannot be directly converted to an integer.


