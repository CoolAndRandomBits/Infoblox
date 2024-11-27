# This script will read a list of hostnames and IPs in CSV format
# and create host entries in IPAM.  Before creating them,
# the script will verify that there isn't a host entry that either
# matches the name or the IP

# Input file should be a CSV file in the following order:
# Hostname, IP
# Check that the file only contains two fields


import requests
import sys
import time




# ==============================================================================
# DEFINE STATIC VARIABLES
# ==============================================================================

BaseURL = "https://<infobloxFQDN>/wapi/v1.4.2/"
SearchByHost = "record:host?name:~="
SearchByIP = "record:host?ipv4addr="



def Verify(argObjSession,argHost,argIP):

    HostSearch = argObjSession.get(BaseURL + SearchByHost + argHost)
    IPsearch = argObjSession.get(BaseURL + SearchByIP + argIP)

    if HostSearch.text != "[]":
        print("Host entry with this name already exists:\n\n")
        print(HostSearch.text)
        print("\n\nSkipping entry\n\n")
        return 1
    else:
        if IPsearch.text != "[]":
            print("Host entry with this IP address already exists:\n\n")
            print(IPsearch.text)
            print("\n\nSkipping entry\n\n")
            #sys.exit()
            return 1
        
    print("\nHost with this entry or IP does not exist\n")

    return 0
        




    

def Worker(argObjSession,argHost,argIP):

    payload = '{\"ipv4addrs\": [{\"ipv4addr\": \"' + argIP + '\"}], \"name\": \"' + argHost + '\"}'
    
    print("\n")

    r = argObjSession.post(BaseURL + "record:host", data=payload)
    HostSearch = argObjSession.get(BaseURL + SearchByHost + argHost)
    
    print("\n\nPOST complete.")    
    print("HTTP status code: ", r.status_code)
    print("HTTP reason: ", r.reason)
    print("JSON result: \n\n" + HostSearch.text)
    
    print("\n\n")
    
 
   







def main():
    
    # Open the file and count how many lines are in it
    # This will be used for the While loop later
    
    txtFile = open("_list.csv", "r")
    NumOfLines = len(txtFile.readlines())

    print("Number of lines in file: %d \n" %(NumOfLines))
    txtFile.close()


    # Open the file for actual usage
    
    txtFile = open("_list.csv", "r")

    # Ask for credentials to Infoblox

    print("\n")
    print("Please enter your Infoblox credentials.\n")
    print("WARNING: Password will be echoed to screen.  Make sure no one is looking.\n")
    Username = input("Username: ")
    Password = input("Password: ")
      
    # Establish a session to the Infoblox API and
    # check the credentials

    objSession = requests.Session()
    objSession.auth = (Username, Password)
    objSession.verify = False

    AuthCheck = objSession.get(BaseURL + "grid")

    if AuthCheck.status_code != 200:
        print("Login failed.  Invalid username and/or password."
              "Please rerun the script using a valid username/password."
              "\n\nFailure reason: \'%d %s\'" % (AuthCheck.status_code, AuthCheck.reason))
        txtFile.close()
        sys.exit()

    Counter = 0

    while Counter < NumOfLines:
        Entry = txtFile.readline().rstrip()
        if Entry is "":
            print("\nEOF reached.  Exiting.")
            txtFile.close()
            objSession.close()
            return
        else:
            print("\n%d - WORKING ON ENTRY: %s\n\n" % (Counter, Entry))

            # Convert the string result to a list
            
            ListEntry = Entry.split(",")

            host = ListEntry[0]
            ip = ListEntry[1]

            # Check whether this entry already exists
            
            verResults = Verify(objSession,host,ip)

            # Create the entry if it doesn't exist
            
            if verResults == 0:
                Worker(objSession,host,ip)
            
            Answer = input("Would you like to continue to the next entry? [y/n] ")
            Answer = Answer.lower()

            while Answer not in ["yes","no","y","n"]:
                Answer = input("Would you like to continue to the next entry? [y/n] ")
                Answer = Answer.lower()    
            if Answer in ["no","n"]:
                print("Terminating.")
                txtFile.close()
                objSession.close()
                sys.exit()
                return
            Counter +=1

    print("\n\nEOF reached.  Exiting.")
    txtFile.close()
    objSession.close()   
    txtFile.close()
    sys.exit()            



# ==============================================================================
# CALL MAIN FUNCTION
# ==============================================================================

main()
