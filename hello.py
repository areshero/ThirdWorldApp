from flask import Flask, request, redirect, session
import twilio.twiml
import googlemaps
from datetime import datetime
import json
from googlemaps import convert
from BeautifulSoup import BeautifulSoup
import googlemaps
from googlemaps import directions as getDirectionsUsingGoogleMap
from google import google
from twitter import *
import os

# The session object makes use of a secret key.
SECRET_KEY = 'a secret key'

# Twitter key
CONSUMER_KEY = 'UL3gpjEYeyVDAzt9UbUJWEZTN'
CONSUMER_SECRET = 'UoqVQytCAjvFqDBHe7vIkISDYqtTtrEpopzb5E6vS2ckNwm5iG'
ACCESS_TOKEN = '3829007953-vSaGe37Wnq0z29hnGro6Y33K3qbxIRwfpNHoMZJ'
ACCESS_TOKEN_SECRET = 'QVTIeDCGUSuIn8wHeqeqN9CpTDVBB2takYRHaXAmCJw5H'

# Twitter
t = Twitter(auth=OAuth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET))

app = Flask(__name__)
app.config.from_object(__name__)
# Try adding your own number to this list!
callers = {
	"+14158675309": "Curious George",
	"+12135097300": "Hehehehhe",
	"+14158675311": "Virgil",
	"+12134001959": "SBLuke",
	"+16412750872": "Yo Shen !",
	"+17348348282": "Yo Yisha! Wha~~~up!"
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
	message = ""

	requestBody = handlerMessageBody()

	from_number = request.values.get('From')
	messageTo = request.values.get('To')
	if not from_number or not messageTo:
		return "No From number or To number"
	if from_number in callers:
		name = callers[from_number]
	else:
		name = "Monkey"
	if 'To' in request.values:
		
		message = "".join(["Body: \n", requestBody, " ...... Hey ", name, " Anything else?"])
	else:
		message = "error"
	return message

def handlerMessageBody():

	commandMessage = "Command: 1. Navigate from {from} to {to}. 2. Google keyword 3. Just reply 'hehe'."

	if 'Body' not in request.values:
		return "No message Body"
	else:
		requestBody = request.values.get('Body').encode('utf-8')
	requestParams = requestBody.split(' ')
	responseMessage = ""
	if len(requestParams) == 0:
		responseMessage = commandMessage

	elif requestParams[0].lower() == "navigate" :
		# Get directions
		# origin = "University of Southern California, Los Angeles, CA"
		# destination = "Galen Center, South Figueroa Street, Los Angeles, CA"
		fromIndex = requestBody.index('from')
		toIndex = requestBody.index('to')
		origin = requestBody[fromIndex+5:toIndex]
		destination = requestBody[toIndex+3:]

		responseMessage = getDirections(origin,destination)
	elif requestParams[0].lower() == "google" :
		keyword = ""
		for item in requestParams[1:]:
			keyword += item
		num_page = 1
		search_results = google.search(keyword, num_page)
		responseMessage = search_results[0].description

	elif requestParams[0].lower() == "hehe" :
		responseMessage = "hehe your sister! zai jian!"
	elif requestParams[0].lower() == "tweet":
		responseMessage = "Twitter updated"
		twitterMessageBody = requestBody[8:]
		t.statuses.update(status=twitterMessageBody)
	else:
		# Give options:
		responseMessage = "Not a valid option." + commandMessage
	return responseMessage

def getDirections(origin,destination):
	gmaps = googlemaps.Client(key='AIzaSyC6ATRDCMZm2hv7Ay2nl3EgA98r2ebKHEQ')
	directionsResult = getDirectionsUsingGoogleMap.directions(gmaps,origin,destination)
	res = ""
	if len(directionsResult) == 0:
		return res
	for index,currStep in enumerate(directionsResult[0]["legs"][0]["steps"]):
		html = currStep["html_instructions"]
		soup = BeautifulSoup(html)
		text_parts = soup.findAll(text=True)
		text = ''.join(text_parts)
		res += str(index+1) +". "+ text + ".\n "

	return res

if __name__ == "__main__":
	app.run(debug=True)
