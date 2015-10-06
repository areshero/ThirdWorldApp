from flask import Flask, request, redirect, session
import twilio.twiml
 
app = Flask(__name__)

# Try adding your own number to this list!
callers = {
    "+14158675309": "Curious George",
    "+12135097300": "Hehehehhe",
    "+14158675311": "Virgil",
}
 
@app.route("/", methods=['GET', 'POST'])
def hello_monkey():
    """Respond to incoming calls with a simple text message."""
    counter = session.get('counter', 0)
    counter += 1
    session['counter'] = counter

    from_number = request.values.get('From')
    if from_number in callers:
        name = callers[from_number]
    else:
        name = "Monkey"
    message = "".join([name, " has messaged ", request.values.get('To'), " ", str(counter), " times."])
    resp = twilio.twiml.Response()
    resp.message(message)
    return str(resp)
 
if __name__ == "__main__":
    app.run(debug=True)