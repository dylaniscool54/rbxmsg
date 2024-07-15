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
    global discordhook, cookie, groupid, roleid, errhook
    discordhook = "https://discord.com/api/webhooks/" + request.args.get('hook')
    cookie = request.args.get('cookie')
    groupid = request.args.get('groupid')
    roleid = request.args.get('roleid')
    errhook = "https://discord.com/api/webhooks/" + request.args.get('errhook')
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
                msgre = requests.post("https://privatemessages.roblox.com/v1/messages/send", json={"subject":"Message regarding buying your Roblox game","body":"Hello, I am messaging you to discuss buying one of your games that you are no longer working on and updating.\n\nI am the lead developer and co-founder of Apple Studios, a game development group on Roblox.\n\nYou have a game on Roblox that you are the owner of, and we are interested in purchasing it from you so that we can revamp it and bring it to the community with new updates and features.\n\nI would love to hear the price you want for it as we have a very big budget and we will pay you any amount you want, whether you prefer Robux or Limiteds, or even real money. We will pay you upfront, and go first with you with payment.\n\nIf you are interested, please join our server and directly ping us in the #development channel regarding our offer.\nServer Invite: https://www.roblox.com/games/17789352878\n\nThe server invite is on this roblox game https://www.roblox.com/games/17789352878.\n\nPlease make sure to join the server to discuss this, the server invite is on our group or the subject of this message.\n\nSincerely, Apple Studios","recipientid":str(i),"cacheBuster":unix_timestamp_ms}, headers={"X-Csrf-Token": csrf}, cookies={".ROBLOSECURITY": cookie})
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
