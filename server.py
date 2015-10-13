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

'''
flight information
in the sea
stock
anything that we need to keep track of anytime
need to sell or buy stock now, right now
'''

# The session object makes use of a secret key.
SECRET_KEY = 'a secret key'

app = Flask(__name__)
app.config.from_object(__name__)

# Try adding your own number to this list!
callers = {
	"+14158675309": "Curious George",
	"+12135097300": "Chong",
	"+14158675311": "Virgil",
	"+12134001959": "Luke",
	"+16412750872": "Yo Shen !",
	"+17348348282": "Yo Yisha!"
}

@app.route("/", methods=['GET', 'POST'])
def root():
	message = handleMessage()
	resp = twilio.twiml.Response()
	#resp.say('Hello !!...... ')
	resp.sms(message)
	return str(resp)

@app.route("/google", methods=['GET', 'POST'])
def doGoogleSearch():
	responseMessage = ""
	if 'Body' not in request.values:
		return "No message Body"
	else:
		requestBody = request.values.get('Body').encode('utf-8')

	requestParams = requestBody.split(' ')
	keyword = ""
	for item in requestParams[1:]:
		keyword += item
	num_page = 1
	search_results = google.search(keyword, num_page)
	if len(search_results) > 0:
		responseMessage = unicode(search_results[0].description, "utf-8")
	else:
		responseMessage = "Error, no such results"
	return responseMessage

@app.route("/navigate", methods=['GET', 'POST'])
def doNavigate():
	responseMessage = ""
	if 'Body' not in request.values:
		return "No message Body"
	else:
		requestBody = request.values.get('Body').encode('utf-8')

	requestParams = requestBody.split(' ')
	fromIndex = requestBody.index('from')
	toIndex = requestBody.index('to')
	origin = requestBody[fromIndex+5:toIndex]
	destination = requestBody[toIndex+3:]

	responseMessage = getDirections(origin,destination)
	return responseMessage

def getTweetClient():
		# Twitter key
	CONSUMER_KEY = 'UL3gpjEYeyVDAzt9UbUJWEZTN'
	CONSUMER_SECRET = 'UoqVQytCAjvFqDBHe7vIkISDYqtTtrEpopzb5E6vS2ckNwm5iG'
	ACCESS_TOKEN = '3829007953-vSaGe37Wnq0z29hnGro6Y33K3qbxIRwfpNHoMZJ'
	ACCESS_TOKEN_SECRET = 'QVTIeDCGUSuIn8wHeqeqN9CpTDVBB2takYRHaXAmCJw5H'

	# Twitter
	t = Twitter(auth=OAuth(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET))
	return t
@app.route("/tweet", methods=['GET', 'POST'])
def doTweet():

	responseMessage = ""
	t = getTweetClient()
	if 'Body' not in request.values:
		return "No message Body"
	else:
		requestBody = request.values.get('Body').encode('utf-8')

	twitterMessageBody = requestBody[8:]
	try:
		t.statuses.update(status=twitterMessageBody)
		responseMessage = "Twitter updated"
	except:
		responseMessage = 'Can not send the message now. Please retry.'
	return responseMessage

def handleMessage():
	counter = session.get('counter', 0)
	counter += 1
	session['counter'] = counter
	message = ""

	responseBody = getResponseBody()

	from_number = request.values.get('From')
	messageTo = request.values.get('To')
	if not from_number or not messageTo:
		return "No From number or To number"
	if from_number in callers:
		name = callers[from_number]
	else:
		name = "Guest"
	if 'To' in request.values:
		message = responseBody
	else:
		message = "error"
	return message

def getResponseBody():

	commandMessage = "Command: \n 1. Navigate from {from} to {to}.\n 2. Google {keyword}.\n 3. Tweet {message}.\n"

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
		# print search_results[0].description
		if len(search_results) > 0:
			responseMessage = unicode(search_results[0].description, "utf-8")
	elif requestParams[0].lower() == "tweet":
		t = getTweetClient()
		responseMessage = "Twitter updated"
		twitterMessageBody = requestBody[5:]
		t.statuses.update(status=twitterMessageBody)
	elif requestParams[0].lower() == "hehe" :
		responseMessage = ":)"
	else:
		# Give options:
		responseMessage = commandMessage
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
		res += str(index+1) +". "+ text +" travelMode: " +currStep["travel_mode"].lower()+", distance: " + currStep["distance"]["text"] +", duration: " +currStep["duration"]["text"]+ ".\n "
	return res

if __name__ == "__main__":
	app.run(debug=True)
