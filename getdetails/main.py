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

    if request_json and "game_id" in request_json:
        game_id = request_json["game_id"]
    elif request_args and "game_id" in request_args:
        game_id = request_args["game_id"]
    else:
        print("Missing parameter 'game_id'")
        return "Missing game_id"

    if request_json and "game_name" in request_json:
        game_name = request_json["game_name"]
    elif request_args and "game_name" in request_args:
        game_name = request_args["game_name"]
    else:
        print("Missing parameter 'game_name'")
        return "Missing game_name"
    
    # pass in the game id, get the game details
    URL = "https://boardgamegeek.com/xmlapi/boardgame/" + urllib.parse.quote(game_id)
    response = requests.get(URL)

    #Validate reponse
    if response.status_code == 200:
        # The request was successful
        # Parse the response body as XML
        xml = ElementTree(fromstring(response.content))
        root = xml.getroot()

    else:
       print(response.status_code)
       print(response.content)
       return 0
    
    game_details = {"name":  game_name,"gameID": game_id}

    for this_game in root.iter('boardgame'):
        # Itterate over values:
        for game_attrib in this_game:
            # Year Published
            if game_attrib.tag == "yearpublished":
               game_details["YearPublished"] = game_attrib.text
            
            # Min Players
            if game_attrib.tag == "minplayers":
               game_details["minplayers"] = game_attrib.text

            # Max Players
            if game_attrib.tag == "maxplayers":
               game_details["maxplayers"] = game_attrib.text

            # Avg PlayTime
            if game_attrib.tag == "playingtime":
               game_details["playingtime"] = game_attrib.text

            # Min Age
            if game_attrib.tag == "age":
               game_details["age"] = game_attrib.text
            
            # description
            if game_attrib.tag == "description":
               game_details["description"] = game_attrib.text

            # image
            if game_attrib.tag == "image":
               game_details["image"] = game_attrib.text  
            
            # thumbnail
            if game_attrib.tag == "thumbnail":
               game_details["thumbnail"] = game_attrib.text  

            if game_attrib.tag == "boardgamecategory":
                if "boardgamecategory" in game_details:
                    game_details["boardgamecategory"] += ";" + game_attrib.text  
                else:
                   game_details["boardgamecategory"] = game_attrib.text
            
            if game_attrib.tag == "boardgamemechanic":
                if "boardgamemechanic" in game_details:
                    game_details["boardgamemechanic"] += ";" + game_attrib.text  
                else:
                   game_details["boardgamemechanic"] = game_attrib.text

    return (json.dumps(game_details))