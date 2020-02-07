## No-IP Dynamic DNS Updater
Python 3 (tested for >=3.6)

Updates No-IP with the current IP address.
The script creates log and data directories in the script directory.
Fill the credentials.txt file with the following information (one per line, no additional characters):
* Kabelbox username
* Kabelbox password
* No-IP hostname
* No-IP user (e-mail address)
* No-IP password

Kabelbox is a router. You will probably need to update the script to your setup. 
For example, getting the IP address from the router could be replaced with a call to whatsmyipaddress.com or any such 
service. 

__If the script receives an error response from No-IP__ 
it will stop making updates until do_update.txt is updated to contain at least "y".  
Make sure to fix the problem before you update do_update.txt.