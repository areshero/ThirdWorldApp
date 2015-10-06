from flask import Flask, request, redirect, session
import twilio.twiml

# The session object makes use of a secret key.
SECRET_KEY = 'a secret key'
app = Flask(__name__)
app.config.from_object(__name__)
# Try adding your own number to this list!
callers = {
    "+14158675309": "Curious George",
    "+12135097300": "Hehehehhe",
    "+14158675311": "Virgil",
}
 
@app.route("/", methods=['GET', 'POST'])
def hello_monkey():

    message = handleMessage()

    resp = twilio.twiml.Response()
    resp.say('Hello monkey!!...... ')
    resp.sms(message)
    return str(resp)

def handleMessage():
    counter = session.get('counter', 0)
    counter += 1
    session['counter'] = counter

    requestBody = handlerMessageBody()

    from_number = request.values.get('From')
    message = ""
    if from_number in callers:
        name = callers[from_number]
    else:
        name = "Monkey"
    if 'To' in request.values:
        messageTo = request.values.get('To')
        message = "".join(["Body: ", requestBody, " ...... ", name, " has messaged ", messageTo, ", ", str(counter), " times."])
    else:
        message = "error"
    return message

def handlerMessageBody():
    requestBody = request.values.get('Body')
    requestList = requestBody.split(" ")
    requestBodyResult = str(requestList[1]) + " " + str(requestList[3])

    return requestBodyResult

if __name__ == "__main__":
    app.run(debug=True)
