from flask import escape
import urllib.parse
from xml.etree.ElementTree import fromstring, ElementTree
import requests
import json

import functions_framework

@functions_framework.http
def hello_http(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and "game_name" in request_json:
        game_name = request_json["game_name"]
    elif request_args and "game_name" in request_args:
        game_name = request_args["game_name"]
    else:
        print("Missing parameter 'game_name'")
        return "Missing game_name"

    if request_json and "only_first" in request_json:
        only_first = request_json["only_first"]
    elif request_args and "only_first" in request_args:
        only_first = request_args["only_first"]
    else:
        only_first = None
    
        # Lookup game id, return top value
    URL = "https://boardgamegeek.com/xmlapi/search?search=" + urllib.parse.quote(game_name)
    response = requests.get(URL)

    #Validate reponse
    if response.status_code == 200:
        # The request was successful
        # Parse the response body as XML
        xml = ElementTree(fromstring(response.content))
        root = xml.getroot()

        # Validate games found
        if len(root) == 0:
           # nothing found
           print(f"Nothing found for {game_name}")
           return "No games found"
    else:
       print(response.status_code)
       print(response.content)
       return {}
    
    foundgames = {}
    for game in root:
        # Lookup Name, there has to a better way to do this
        game_name = "Not Found"
        for AValue in game:
           if AValue.tag == "name":
            game_name = AValue.text

        # Add to game list
        foundgames[game.attrib['objectid']] = game_name

    # Output results
    if only_first is None:
       return json.dumps(foundgames)
    else:
        return json.dumps(foundgames.popitem())