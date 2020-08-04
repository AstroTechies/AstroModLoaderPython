# original https://github.com/ricky-davis/AstroLauncher/blob/master/cogs/AstroAPI.py

import requests

base_headers = {'Content-Type': 'application/json; charset=utf-8',
                'X-PlayFabSDK': 'UE4MKPL-1.19.190610',
                'User-Agent': 'game=Astro, engine=UE4, version=4.18.2-0+++UE4+Release-4.18, platform=Windows, osver=6.2.9200.1.256.64bit'
                }


def generate_XAUTH(serverGUID):
    url = "https://5EA1.playfabapi.com/Client/LoginWithCustomID?sdk=UE4MKPL-1.19.190610"
    requestObj = {
        "CreateAccount": True,
        "CustomId": serverGUID,
        "TitleId": "5EA1"
    }
    x = (requests.post(url, headers=base_headers, json=requestObj)).json()
    return x['data']['SessionTicket']


def get_servers(ipPortCombo, headers):
    url = 'https://5EA1.playfabapi.com/Client/GetCurrentGames?sdk=UE4MKPL-1.19.190610'
    requestObj = {
        """TagFilter": {
            "Includes": [
                {"Data": {"gameId": ipPortCombo}}
            ]
        }"""
    }
    x = (requests.post(url, headers=headers, json=requestObj)).json()
    return x



