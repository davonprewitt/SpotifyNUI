import json
from flask import Flask, request, redirect, g, render_template
import requests
import base64
import urllib
import cv2
import numpy as np
import math
from GestureAPI import *
import requests
# import os


# # Variables & parameters
# hsv_thresh_lower=150
# gaussian_ksize=11
# gaussian_sigma=0
# morph_elem_size=13
# median_ksize=3
# capture_box_count=9
# capture_box_dim=20
# capture_box_sep_x=8
# capture_box_sep_y=18
# capture_pos_x=500
# capture_pos_y=150
# cap_region_x_begin=0.5 # start point/total width
# cap_region_y_end=0.8 # start point/total width
# finger_thresh_l=2.0
# finger_thresh_u=3.8
# radius_thresh=0.04 # factor of width of full frame
# first_iteration=True
# finger_ct_history=[0,0]


# Authentication Steps, paramaters, and responses are defined at https://developer.spotify.com/web-api/authorization-guide/
# Visit this url to see all the steps, parameters, and expected response. 


app = Flask(__name__)

#  Client Keys
CLIENT_ID = "8c3d7ae5971e4b2a87d02fa1c6e332b8"
CLIENT_SECRET = "d35c1823baac42819e30f8926bf5724e"

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)


# Server-side Parameters
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 8080
REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
SCOPE = "user-modify-playback-state user-read-currently-playing"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()


auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID
}

@app.route("/")
def index():
    # Auth Step 1: Authorization
    url_args = "&".join(["{}={}".format(key,urllib.quote(val)) for key,val in auth_query_parameters.iteritems()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)


@app.route("/callback/q")
def callback():
    # Auth Step 4: Requests refresh and access tokens
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI
    }
    base64encoded = base64.b64encode("{}:{}".format(CLIENT_ID, CLIENT_SECRET))
    headers = {"Authorization": "Basic {}".format(base64encoded)}
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload, headers=headers)

    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    # Auth Step 6: Use the access token to access Spotify API
    authorization_header = {"Authorization":"Bearer {}".format(access_token)}
    authorization_header_str = json.dumps(authorization_header)

    # Get profile data
    user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
    profile_response = requests.get(user_profile_api_endpoint, headers=authorization_header)
    profile_data = json.loads(profile_response.text)

    # Get user playlist data
    playlist_api_endpoint = "{}/playlists".format(profile_data["href"])

    playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
    playlist_data = json.loads(playlists_response.text)
    
    ###########

    pause_play_endpoint = "{}".format(SPOTIFY_API_URL)
    f = open('auth.txt', 'w')
    f.write(access_token + "\n" + pause_play_endpoint)
    # pause_play_endpoint_response = requests.put(pause_play_endpoint, headers=authorization_header)
    # print "Status_Begin"
    # print pause_play_endpoint_response.text
    # print "Status_End"
    ###########
    # Combine profile and playlist data to display
    user = profile_data["id"] #+ playlist_data["items"]
    print user
    return render_template("index.html",user=user)





if __name__ == "__main__":
    app.run(debug=True,port=PORT)

