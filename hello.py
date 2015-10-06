from flask import Flask, request, redirect, session
import twilio.twiml
import googlemaps
from datetime import datetime
import json
from googlemaps import convert
import html2text


#AIzaSyC6ATRDCMZm2hv7Ay2nl3EgA98r2ebKHEQ

# The session object makes use of a secret key.
SECRET_KEY = 'a secret key'
app = Flask(__name__)
app.config.from_object(__name__)
# Try adding your own number to this list!
callers = {
	"+14158675309": "Curious George",
	"+12135097300": "Hehehehhe",
	"+14158675311": "Virgil",
	"+12134001959": "SBLuke",
	"+16412750872": "Yo Shen !"
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

	requestBody = handlerMessageBody()

	from_number = request.values.get('From')
	messageTo = request.values.get('To')
	message = ""
	if from_number in callers:
		name = callers[from_number]
	else:
		name = "Monkey"
	if 'To' in request.values:
		
		message = "".join(["Body: ", requestBody, " ...... ", name, " has messaged ", messageTo, ", ", str(counter), " times."])
	else:
		message = "error"
	return message

def handlerMessageBody():
	requestBody = request.values.get('Body').encode('utf-8')     
	requestParams = requestBody.split(' ')
	responseMessage = ""
	if len(requestParams) == 0:
		responseMessage = "Yo. Welcome to xxx. There are several options you can have: 1. Navigate from {from} to {to}. 2. Just reply 'hehe'."

	elif requestParams[0].lower() == "navigate" :
		# Get directions
		origin = "University of Southern California, Los Angeles, CA"
		destination = "Galen Center, South Figueroa Street, Los Angeles, CA"
		responseMessage = getDirections(origin,destination)
	elif requestParams[0].lower() == "hehe" :
		responseMessage = "hehe your sister! zai jian!"
	else:
		# Give options:
		responseMessage = "Yo. Welcome to xxx. There are several options you can have: 1. Navigate from {from} to {to}. 2. Just reply 'hehe'."
	return responseMessage

def getDirections(origin,destination):
	gmaps = googlemaps.Client(key='AIzaSyC6ATRDCMZm2hv7Ay2nl3EgA98r2ebKHEQ')
	directionsResult = directions(gmaps,origin,destination)
	res = ""
	for index,currStep in enumerate(directionsResult[0]["legs"][0]["steps"]):
		res += str(index+1) + html2text.html2text(currStep["html_instructions"])
	print res
	return res
'''
	geocode_result = gmaps.geocode('USC')
	# Look up an address with reverse geocoding
	#reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))

	# Request directions via public transit
	nowDatetime = datetime.now()
	directions_result = gmaps.directions("Galen Center", "Los Angeles, CA", mode="driving", departure_time=nowDatetime)
	print json.dumps(directions_result)
'''

def directions(client, origin, destination,
			   mode=None, waypoints=None, alternatives=False, avoid=None,
			   language=None, units=None, region=None, departure_time=None,
			   arrival_time=None, optimize_waypoints=False, transit_mode=None,
			   transit_routing_preference=None):
	"""Get directions between an origin point and a destination point.
	:param origin: The address or latitude/longitude value from which you wish
			to calculate directions.
	:type origin: string or dict or tuple
	:param destination: The address or latitude/longitude value from which
		you wish to calculate directions.
	:type destination: string or dict or tuple
	:param mode: Specifies the mode of transport to use when calculating
		directions. One of "driving", "walking", "bicycling" or "transit"
	:type mode: string
	:param waypoints: Specifies an array of waypoints. Waypoints alter a
		route by routing it through the specified location(s).
	:param alternatives: If True, more than one route may be returned in the
		response.
	:type alternatives: bool
	:param avoid: Indicates that the calculated route(s) should avoid the
		indicated features.
	:type avoid: list or string
	:param language: The language in which to return results.
	:type language: string
	:param units: Specifies the unit system to use when displaying results.
		"metric" or "imperial"
	:type units: string
	:param region: The region code, specified as a ccTLD ("top-level domain"
		two-character value.
	:type region: string
	:param departure_time: Specifies the desired time of departure.
	:type departure_time: int or datetime.datetime
	:param arrival_time: Specifies the desired time of arrival for transit
		directions. Note: you can't specify both departure_time and
		arrival_time.
	:type arrival_time: int or datetime.datetime
	:param optimize_waypoints: Optimize the provided route by rearranging the
		waypoints in a more efficient order.
	:type optimize_waypoints: bool
	:param transit_mode: Specifies one or more preferred modes of transit.
		This parameter may only be specified for requests where the mode is
		transit. Valid values are "bus", "subway", "train", "tram", "rail".
		"rail" is equivalent to ["train", "tram", "subway"].
	:type transit_mode: string or list of strings
	:param transit_routing_preference: Specifies preferences for transit
		requests. Valid values are "less_walking" or "fewer_transfers"
	:type transit_routing_preference: string
	:rtype: list of routes
	"""

	params = {
		"origin": _convert_waypoint(origin),
		"destination": _convert_waypoint(destination)
	}

	if mode:
		# NOTE(broady): the mode parameter is not validated by the Maps API
		# server. Check here to prevent silent failures.
		if mode not in ["driving", "walking", "bicycling", "transit"]:
			raise ValueError("Invalid travel mode.")
		params["mode"] = mode

	if waypoints:
		waypoints = convert.as_list(waypoints)
		waypoints = [_convert_waypoint(waypoint) for waypoint in waypoints]

		if optimize_waypoints:
			waypoints = ["optimize:true"] + waypoints

		params["waypoints"] = convert.join_list("|", waypoints)

	if alternatives:
		params["alternatives"] = "true"

	if avoid:
		params["avoid"] = convert.join_list("|", avoid)

	if language:
		params["language"] = language

	if units:
		params["units"] = units

	if region:
		params["region"] = region

	if departure_time:
		params["departure_time"] = convert.time(departure_time)

	if arrival_time:
		params["arrival_time"] = convert.time(arrival_time)

	if departure_time and arrival_time:
		raise ValueError("Should not specify both departure_time and"
						 "arrival_time.")

	if transit_mode:
		params["transit_mode"] = convert.join_list("|", transit_mode)

	if transit_routing_preference:
		params["transit_routing_preference"] = transit_routing_preference

	return client._get("/maps/api/directions/json", params)["routes"]

def _convert_waypoint(waypoint):
	if not convert.is_string(waypoint):
		return convert.latlng(waypoint)

	return waypoint

if __name__ == "__main__":
	app.run(debug=True)
