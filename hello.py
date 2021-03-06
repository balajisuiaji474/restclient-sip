from flask import Flask, request, jsonify, json
from collections import defaultdict
app = Flask(__name__)

def get_def_dict():
    return {'accept':[],'pending':[]}

logins = defaultdict(dict)
logins_id = 1
login_expires = 3600
calls = defaultdict(dict)
calls_id = 1
users = defaultdict(dict)
invites = defaultdict(get_def_dict)

@app.route("/")
def hello():
    result ={}
    result['status']="Restful interface for sip"
    return jsonify(result)

@app.route("/login/<emailid>", methods = ['GET'])
def login_locations(emailid):
    global logins
    result = {}
    if emailid not in logins:
        result['status'] = 'User does not exist'
    else:
        temp=[]
        for item in logins[emailid]['locations']:
            temp_location = {}
            temp_location['id']=item
            temp_location['contact']= logins[emailid]['locations'][item]['contact']
            temp.append(temp_location)
        result['locations']=temp
    return jsonify(result)

@app.route("/login/<emailid>/<userid>", methods = ['DELETE'])
def login_delete(emailid, userid):
    global logins
    global login_expires
    result = {}
    if emailid not in logins:
        result['status'] = 'User does not exist'
    else:
        if int(userid) not in logins[emailid]['locations']:
            result['status'] = 'User id does not exist'
        else:
            logins[emailid]['locations'].pop(int(userid))
            result['status']='User Registration successfull'
    return jsonify(result)

@app.route("/login/<emailid>/<userid>", methods = ['PUT'])
def login_refresh(emailid, userid):
    global logins
    global login_expires
    result = {}
    if emailid not in logins:
        result['status'] = 'User does not exist'
    else:
        if int(userid) not in logins[emailid]['locations']:
            result['status'] = 'User id does not exist'
        else:
            current_location = logins[emailid]['locations'][int(userid)]
            current_location['expires']=login_expires
            result['status']='Registration refresh success'
    return jsonify(result)

@app.route("/login/<emailid>", methods = ['POST'])
def login_registration(emailid):
    global logins_id
    global logins
    global login_expires
    result = {}

    if 'Contact' not in request.headers:
        result['status'] = 'Contact details does not exist, require contact details'
        return jsonify(result)

    if emailid not in logins:
        location = {}
        location['url']='/login/'+emailid
        location['id'] = logins_id
        location['expires'] = login_expires
        logins[emailid] = {}
        temp = location.copy()
        location['contact']= request.headers['Contact']
        logins[emailid]['locations'] ={logins_id:location}
        logins_id+=1
        result = temp
    else:
        current_login = logins[emailid]
        login_exist = False
        for item in current_login['locations']:
            if current_login['locations'][item]['contact'] == request.headers['Contact']:
                result['status']='User location already exist'
            else:
                location = {}
                location['url']='/login/'+emailid
                location['id'] = logins_id
                location['expires'] = login_expires
                logins[emailid] = {}
                temp = location.copy()
                location['contact']= request.headers['Contact']
                logins[emailid]['locations'][logins_id] = location
                logins_id+=1
                result = temp
    return jsonify(result)

@app.route("/call", methods = ['POST'])
def call_setup():
    global calls, calls_id
    result ={}
    if len(request.headers['Subject']) <= 0:
        result['status'] = 'Topic is required to setup the call'
    else:
        temp_call={}
        temp_call['id']=calls_id
        temp_call['url']='/call/'+str(calls_id)
        result = temp_call.copy()
        calls[calls_id]=temp_call
        temp_call['subject']= request.headers['Subject']
        temp_call['children']=[]
        calls_id+=1
    return jsonify(result)

@app.route("/call/<call_id>", methods = ['POST'])
def add_user_to_a_call(call_id):
    global calls
    result ={}
    if int(call_id) not in calls:
        result['status'] = 'Call id does not exist'
    else:
        current_user = request.headers['url']
        if len(current_user) <=0:
            result['status'] = 'User login url is missing.'
        else:
            if current_user not in calls[int(call_id)]['children']:
                calls[int(call_id)]['children'].append(current_user)
            result['status'] = 'Successfully joined call.'
    return jsonify(result)

@app.route("/call/<call_id>", methods = ['DELETE'])
def call_revoke(call_id):
    global calls
    result ={}
    if int(call_id) not in calls:
        result['status'] = 'Call id does not exist'
    else:
        calls.pop(int(call_id))
        result['status'] = 'End call successfull'
    return jsonify(result)

@app.route("/call", methods = ['GET'])
def get_calls():
    global calls
    result ={}
    if len(calls) <=0:
        result['status'] = 'Conference calls not exist'
    else:
        result['scheduled_calls']= ['/call/'+str(i) for i in calls]
    return jsonify(result)

@app.route("/call/<call_id>", methods = ['GET'])
def get_call_details(call_id):
    global calls, calls_id
    result ={}
    if int(call_id) not in calls:
        result['status'] = 'Call id does not exist'
    else:
        result['children']= calls[int(call_id)]['children']
    return jsonify(result)

@app.route("/user", methods = ['POST'])
def add_user():
    global users
    result={}
    current_email=''
    if 'Email' in request.headers:
        current_email = request.headers['Email']
    if len(current_email) <= 0:
        result['status'] = 'Valid email address is required'
    else:
        if current_email not in users:
            tmp={}
            tmp['id']=current_email
            tmp['url']='/user/'+current_email
            result = tmp.copy()
            tmp['messages'] = []
            users[current_email]=tmp
        else:
            result['id']=users[current_email]['id']
            result['url']=users[current_email]['url']
    return jsonify(result)

@app.route("/user/message/<email>", methods = ['POST'])
def add_user_message(email):
    global users
    result={}
    current_message=''
    if 'Message' in request.headers:
        current_message = request.headers['Message']
    if len(current_message) <= 0:
        result['status'] = 'Valid message is required'
    else:
        if email not in users:
            result['status'] = 'User does not exist'
        else:
            if current_message not in users[email]['messages']:
                users[email]['messages'].append(current_message)
            result['status'] = 'Message added to the user'
    return jsonify(result)

@app.route("/user/message/<email>", methods = ['GET'])
def get_user_message(email):
    global users
    result={}

    if email not in users:
        result['status'] = 'User does not exist'
    else:
        if len(users[email]['messages']) == 0:
            result['status'] = 'Message does not exist for the user'
        else:
            result['messages']=users[email]['messages']
    return jsonify(result)

@app.route("/invite/<email_id>", methods = ['POST'])
def add_invite(email_id):
    global invites, calls
    result = {}
    invite_to = ''
    command = ''
    call_url = ''
    if 'To' in request.headers:
        invite_to = request.headers['To']
    if 'Command' in request.headers:
        command = request.headers['Command']
    if 'url' in request.headers:
        call_url = request.headers['url']
    if len(command)<=0:
        result['status']='Type of invite is missing'
        return jsonify(result)
    if command !='accept' and command!='reject' and len(invite_to)<=0:
        result['status']='Invite recepient is missing'
        return jsonify(result)
    if len(call_url)<=0:
        result['status']='Call url is missing'
        return jsonify(result)
    if email_id not in logins:
        result['status']='Invite sender does not exist'
        return jsonify(result)
    if command !='accept' and command!='reject' and invite_to not in logins:
        result['status']='Invite recepient does not exist'
        return jsonify(result)

    if command == 'invite' and call_url not in invites[invite_to]['pending']:
        invites[invite_to]['pending'].append(call_url)
        result['status']='Call invite sent'
        return jsonify(result)
    elif command == 'invite':
        result['status']='Call invite already exist'
        return jsonify(result)

    if command == 'accept' and call_url not in invites[email_id]['pending']:
        result['status']='Call invite does not exist'
        return jsonify(result)
    elif command == 'accept' and call_url in invites[email_id]['pending']:
        invites[email_id]['pending'].remove(call_url)
        invites[email_id]['accept'].append(call_url)
        current_call_id = int(call_url.split('/call/')[1])
        calls[current_call_id]['children'].append('/login/'+email_id)
        result['status']='Call invite accepted'
        return jsonify(result)

    if command == 'reject' and call_url not in invites[email_id]['pending']:
        result['status']='Call invite does not exist'
        return jsonify(result)
    elif command == 'reject' and call_url in invites[email_id]['pending']:
        invites[email_id]['pending'].remove(call_url)
        result['status']='Call invite rejected'
        return jsonify(result)
    result['status'] ='Operation not supported'
    return jsonify(result)

@app.route("/invite/<email_id>", methods = ['GET'])
def get_accept_invites(email_id):
    result = {}
    if email_id in invites and len(invites[email_id]['accept'])<=0:
        result['status'] = 'User does not have any invites'
    elif email_id not in invites and email_id not in logins:
        result['status'] = 'User does not exist'
    elif email_id not in invites and email_id in logins:
        result['status'] = 'User does not have any invites'
    else:
        result['calls_accepted'] = invites[email_id]['accept']
    return jsonify(result)

@app.route("/invite/pending/<email_id>", methods = ['GET'])
def get_pending_invites(email_id):
    result = {}
    if email_id in invites and len(invites[email_id]['pending'])<=0:
        result['status'] = 'User does not have any pending invites'
    elif email_id not in invites and email_id not in logins:
        result['status'] = 'User does not exist'
    elif email_id in logins and email_id not in invites:
        result['status'] = 'User does not have any pending invites'
    else:
        result['pending_invites'] = invites[email_id]['pending']
    return jsonify(result)


if __name__ == "__main__":
    app.run()
