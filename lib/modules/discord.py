import json
import pickle
import sqlite3
import time
import uuid

import requests

from ..db import db

# Code specific to communicating with the Discord API.

# The following methods all facilitate OAuth2 communication with Discord.
# See https://discord.com/developers/docs/topics/oauth2 for more details.

# Generate the url which the user will be directed to in order to approve the
# bot, and see the list of requested scopes.
client_id = ""
client_secret = ""
redirect_uri = ""

with open("./lib/bot/bot_client_id.0", "r", encoding="utf-8") as tokenFile:
    client_id = tokenFile.read()

with open("./lib/bot/bot_client_secret.0", "r", encoding="utf-8") as tokenFile:
    client_secret = tokenFile.read()

with open("./lib/bot/bot_direct_uri.0", "r", encoding="utf-8") as tokenFile:
    redirect_uri = tokenFile.read()


class discordhelper:
    def get_oauth_url():
        state = str(uuid.uuid4().hex)

        url = "https://discord.com/api/oauth2/authorize"
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "state": state,
            "scope": "role_connections.write identify",
            "prompt": "consent",
        }
        return f"{url}?{requests.compat.urlencode(params)}"

    # Given an OAuth2 code from the scope approval page, make a request to Discord's
    # OAuth2 service to retrieve an access token, refresh token, and expiration.
    def get_oauth_tokens(code):
        url = "https://discord.com/api/v10/oauth2/token"
        body = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        }

        response = requests.post(url, data=body)
        if response.ok:
            data = response.json()
            return data
        else:
            raise Exception(
                f"Error fetching OAuth tokens: [{response.status_code}] {response.text}"
            )

    # The initial token request comes with both an access token and a refresh
    # token.  Check if the access token has expired, and if it has, use the
    # refresh token to acquire a new, fresh access token.
    def get_access_token(user_id, tokens):
        if int(time.time()) > int(tokens["expires_in"]):
            url = "https://discord.com/api/v10/oauth2/token"
            body = {
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "refresh_token",
                "refresh_token": tokens["refresh_token"],
            }
            response = requests.post(url, data=body)
            if response.ok:
                tokens = response.json()
                tokens["access_token"] = tokens["access_token"]
                tokens["expires_at"] = time.time() + tokens["expires_in"]

                binary_data = sqlite3.Binary(pickle.dumps(tokens))
                db.execute(
                    "UPDATE oauthcontainer SET Token = ? WHERE UserID = ?",
                    binary_data,
                    user_id,
                )
                db.commit()

                return tokens["access_token"]
            else:
                raise Exception(
                    f"Error refreshing access token: [{response.status_code}] {response.text}"
                )
        return tokens["access_token"]

    # Given a user based access token, fetch profile information for the current user.
    def get_user_data(tokens):
        url = "https://discord.com/api/v10/oauth2/@me"
        headers = {
            "Authorization": f"Bearer {tokens}",
        }
        response = requests.get(url, headers=headers)
        if response.ok:
            data = response.json()
            return data
        else:
            raise Exception(
                f"Error fetching user data: [{response.status_code}] {response.text}"
            )

    # Given metadata that matches the schema, push that data to Discord on behalf
    # of the current user.
    def push_metadata(user_id, tokens, metadata):
        # GET/PUT /users/@me/applications/:id/role-connection
        url = f"https://discord.com/api/v10/users/@me/applications/{client_id}/role-connection"
        access_token = discordhelper.get_access_token(user_id, tokens)
        body = {
            "platform_name": "PWNED 3",
            "metadata": metadata,
        }
        response = requests.put(
            url,
            data=json.dumps(body),
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
        )
        if not response.ok:
            raise Exception(
                f"Error pushing discord metadata: [{response.status_code}] {response.text}"
            )

    # Fetch the metadata currently pushed to Discord for the currently logged
    # in user, for this specific bot.
    def get_metadata(user_id, tokens):
        # GET/PUT /users/@me/applications/:id/role-connection
        url = f"https://discord.com/api/v10/users/@me/applications/{client_id}/role-connection"
        access_token = discordhelper.get_access_token(user_id, tokens)
        response = requests.get(
            url, headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.ok:
            data = response.json()
            return data
        else:
            raise Exception(
                f"Error getting discord metadata: [{response.status_code}] {response.text}"
            )
