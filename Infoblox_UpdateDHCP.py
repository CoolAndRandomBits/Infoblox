import requests
import json
import sys
import time



def WriteToFile(argDHCPmembsOld, argDHCPmembsNew, argPutStatusCode, argPutStatusReason):

    RecordFile.write(argDHCPmembsOld['_ref'] + "," + argDHCPmembsOld['network_view'] + "," + argDHCPmembsOld['network'] + "," +
                        argDHCPmembsOld.get('name', 'No name value') + "," + argDHCPmembsOld.get('comment', 'No comment value') + "," +
                        argDHCPmembsOld['start_addr'] + "," + argDHCPmembsOld['end_addr'] + "," + argDHCPmembsOld['server_association_type'] + "," +
                        argDHCPmembsOld['member']['name'] + "," + argDHCPmembsOld['member']['ipv4addr'] + "," + argPutStatusCode + "," +
                        argPutStatusCode + "," + argPutStatusReason + "," + argDHCPmembsNew['member']['name'] + "," + argDHCPmembsNew['member']['ipv4addr'] + "\n")







def Worker(argDHCPref, argObjSession):

    DHCPmembsOld = argObjSession.get(BaseURL + argDHCPref + GetFields)

    DictDHCPmembsOld = DHCPmembsOld.json()
  
    if DictDHCPmembsOld['server_association_type'] == 'MEMBER':    
        objAPIput = argObjSession.put(BaseURL + argDHCPref + GetFields, data=jsonDHCPmembers)
        PutStatusCode = str(objAPIput.status_code)
 
    else:
        PutStatusCode = "0"
        PutStatusReason = "NA"    

    DHCPmembsNew = argObjSession.get(BaseURL + argDHCPref + GetFields)

    DictDHCPmembsNew = DHCPmembsNew.json()
    
    PutStatusCode = str(objAPIput.status_code)
    StatusReason = objAPIput.reason
    
    WriteToFile(DictDHCPmembsOld, DictDHCPmembsNew, PutStatusCode, StatusReason)




    


def main():
    DHCPfile = open("_infoblox_DHCP_list.txt", "r")
    NumOfLines = len(DHCPfile.readlines())
    print("Number of lines in file: %d \n" %(NumOfLines))
    DHCPfile.close()
    DHCPfile = open("_infoblox_DHCP_list.txt", "r")

    Username = input("Please enter your Infoblox credentials.\nWARNING: Password will be echoed to screen. "
                     "Make sure no one is looking!\n\nUsername: ")
    Password = input("Password: ")

    objSession = requests.Session()
    objSession.auth = (Username, Password)
    objSession.verify = False

    AuthCheck = objSession.get(BaseURL + "grid")

    if AuthCheck.status_code != 200:
        print("Login failed.  Invalid username and/or password."
              "Please rerun the script using a valid username/password."
              "\n\nFailure reason: \'%d %s\'" % (AuthCheck.status_code, AuthCheck.reason))
        DHCPfile.close()
        sys.exit()

    Counter2 = 0
    MaxIterate = 100
    Counter4 = 0        

    if NumOfLines > 10:
            while Counter4 < (NumOfLines + 10):
                while Counter2 < MaxIterate:
                    DHCPref = DHCPfile.readline()
                    if DHCPref is "":
                        print("EOF reached.  Exiting.")
                        DHCPfile.close()
                        objSession.close()
                        return
                    else:
                        print("%d - WORKING ON DHCP RANGE: %s" % (Counter2, DHCPref))
                        Worker(DHCPref, objSession)
                        Counter2 += 1
                Answer = input("%s count reached.\nWould you like to continue with the next cycle? [y/n] " % (MaxIterate))
                Answer = Answer.lower()
                while Answer not in ["yes","no","y","n"]:
                    Answer = input("Would you like to continue with the next cycle? [y/n] ")
                    Answer = Answer.lower()    
                if Answer in ["no","n"]:
                    print("Terminating.")
                    DHCPfile.close()
                    objSession.close()
                    return
                MaxIterate = MaxIterate + 10
                Counter4 += 10
    else:
        print("\nFewer than %s lines" % (MaxIterate))
        DHCPref = DHCPfile.readline()
        while DHCPref != "":
            Worker(DHCPref, objSession)
            DHCPref = DHCPfile.readline()


    DHCPfile.close()
    objSession.close()







# ==============================================================================
# DEFINE STATIC VARIABLES
# ==============================================================================


BaseURL = "https://<infobloxFQDN>/wapi/v1.4.2/"
GetFields= "?_return_fields%2b=name,comment,member,server_association_type"

jsonDHCPmembers= """
{
     "member":
        {
           "_struct": "dhcpmember",
           "ipv4addr" : "1.1.1.1"
        }
}
"""

localtime = time.localtime(time.time())

year = str(localtime.tm_year)
month = str(localtime.tm_mon)
day = str(localtime.tm_mday)
hour = str(localtime.tm_hour)
minute = str(localtime.tm_min)
seconds = str(localtime.tm_sec)

dateStamp = "_" + year + "-" + month + "-" + day + "_" + hour + minute + seconds

RecordFile = open("_infoblox_DHCP_records_%s.csv" % (dateStamp), "w")




# ==============================================================================
# CALL MAIN FUNCTION
# ==============================================================================

main()
RecordFile.close()
