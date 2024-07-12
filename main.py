import requests
import random
from datetime import datetime
import threading
import time
from flask import Flask, request, jsonify

discordhook = ""
cookie = ""
groupid = ""
roleid = ""
errhook = ""
groupname = ""

app = Flask(__name__)


def getcsrf(cookie):
  r = requests.post("https://friends.roblox.com/v1/users/1/unfriend", cookies={".ROBLOSECURITY": cookie})
  return r.headers["x-csrf-token"]


targetuserds = []
cantmessage = []

def findtargetaccount():
    global targetuserds, runs, discordhook, cookie, groupid, roleid, errhook
    nextcur = ""
    while True:
        if not groupid or not roleid:
            print("waiting for serve gid")
            time.sleep(1)
            continue
            
        usersreq = requests.get("https://groups.roblox.com/v1/groups/"+str(groupid)+"/roles/"+str(roleid)+"/users?cursor="+nextcur+"&limit=50&sortOrder=Desc")
        if usersreq.ok:
          users = usersreq.json()
          userids = users["data"]
          for i in userids:
              targetuserds.append(i["userId"])
          nextcur = users["nextPageCursor"]
          if not nextcur:
            nextcur = ""
          if len(userids) == 0:
            runs = 0
            nextcur = ""
            targetuserds = []
        else:
          print(usersreq.status_code)
          print(usersreq.text)
          runs = 0
          nextcur = ""
          targetuserds = []
          
threading.Thread(target=findtargetaccount).start()

@app.route('/info', methods=['GET'])
def info():
    global discordhook, cookie, groupid, roleid, errhook, groupname
    discordhook = "https://discord.com/api/webhooks/" + request.args.get('hook')
    cookie = request.args.get('cookie')
    groupid = request.args.get('groupid')
    roleid = request.args.get('roleid')
    errhook = "https://discord.com/api/webhooks/" + request.args.get('errhook')
    groupname = requests.get("https://groups.roblox.com/v1/groups/" + str(groupid)).json()["name"]
    return "ok"


def mainloop():
    global discordhook, cookie, groupid, roleid, errhook
    while True:
        if not cookie or not discordhook:
            print("waiting for serve")
            time.sleep(1)
            continue
            
        time.sleep(1)

        for i in targetuserds:
            try:
              targetuserds.remove(i)
            except:
              pass
            
            if i in cantmessage:
                continue
            response = requests.get("https://www.roblox.com/users/"+str(i)+"/profile", cookies={".ROBLOSECURITY": cookie})
            print(i)

            if "data-canmessage=true" in response.text:
                print("Found " + str(i))
                csrf = getcsrf(cookie)
                print("Can Message!!!")
                current_time_seconds = time.time()
                unix_timestamp_ms = int(current_time_seconds * 1000)
                msgre = requests.post("https://privatemessages.roblox.com/v1/messages/send", json={"subject":"Winner!","body":"Hello!\nThank you for joining the "+groupname+" Roblox group You were picked out of 100 people to join our exclusive server.\n\nPlease check the social links in: https://www.roblox.com/games/18439349109","recipientid":str(i),"cacheBuster":unix_timestamp_ms}, headers={"X-Csrf-Token": csrf}, cookies={".ROBLOSECURITY": cookie})
                print(msgre)
                print(msgre.text)
                if msgre.ok:
                  if msgre.json()["success"] == True:
                    r = requests.post(discordhook, json={"content": "Sent message to https://www.roblox.com/users/"+str(i)+"/profile"})
                    print(r)
                    cantmessage.append(i)
                  else:
                    requests.post(errhook, json={"content": "code: "+str(msgre.status_code)+", " + msgre.text})
                else:
                  requests.post(errhook, json={"content": "code: "+str(msgre.status_code)+", " + msgre.text})
                    
            else:
                cantmessage.append(i)
            
threading.Thread(target=mainloop).start()

if __name__ == '__main__':
    app.run(port=3000)
