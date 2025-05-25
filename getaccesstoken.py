from dotenv import load_dotenv
import os
import urllib
import requests
load_dotenv(override=True)#loads all env variables into the system path



session = requests.session()


def get_access_token():#This function is responsible for handling the Auth part of the script
    refresh_token = os.getenv("REFRESH_TOKEN").strip()
    client_id = os.getenv("CLIENT_ID").strip()
    client_secret = os.getenv("CLIENT_SECRET").strip()
    url = "https://accounts.zoho.com/oauth/v2/token"
    payload = urllib.parse.urlencode({
    "refresh_token": refresh_token,
    "client_id": client_id,
    "client_secret": client_secret,
    "grant_type": "refresh_token"
})
    header = {
         "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        response = session.post(url=url,data=payload,headers=header)
        access_token = response.json().get("access_token")
        print(access_token)
        if access_token:
            print("Access token obtained successfully.",access_token),
            return access_token
        else:
            print("Access token not found in the response.")
            return False
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Response: {response.text}")
        return False
    except requests.exceptions.RequestException as err:
        print(f"Request error: {err}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False      