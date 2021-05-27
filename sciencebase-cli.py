
import click
import os
import json
from pathlib import Path
from sb3 import auth, querys, client
import requests
from requests_toolbelt.utils import dump
import pprint

CONFIG_FILE_NAME = '.test.json'
pp = pprint.PrettyPrinter(indent=4)
GRAPHQL_URL = 'https://api-beta.staging.sciencebase.gov/graphql'
# GRAPHQL_URL="http://localhost:4000/graphql"

@click.group()
def cli():
    pass


@cli.command()
@click.option('--username', prompt=True, default=lambda: (os.environ.get('USER') + "@contractor.usgs.gov") if os.environ.get('USER') else None)
@click.option('--password', prompt=True, hide_input=True)
@click.option('--debug', 'debug', flag_value=True, default=False)
def login(username, password, debug):
    try:
        authenticator = keycloak_login(username, password, debug)

        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        pprint.pprint(authenticator)
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

        value = {
            "username": username,
            "token": authenticator.get_access_token(),
            "refresh_token": authenticator.get_refresh_token(),
            "client_id": authenticator.keycloak_client_config.client_id,
            "token_server_uri": authenticator.keycloak_client_config.token_server_uri
        }
        with open(CONFIG_FILE_NAME, 'w') as f:
            f.write(json.dumps(value))
        click.echo('logging using %s' % (username, ))
    except Exception:
        click.echo('logging failed for %s' % (username, ))

@cli.command()
@click.option('--debug', 'debug', flag_value=True, default=False)
def refresh(debug):
    with open(CONFIG_FILE_NAME) as f:
        base_data = f.readline()

    bs_data = ''.join(base_data)
    read_data = json.loads(bs_data)

    data = {
            "client_id": read_data["client_id"],
            "grant_type": "refresh_token", 
            "refresh_token": read_data["refresh_token"]
    }
    token_resp = requests.post(read_data["token_server_uri"], data=data)
    if debug:
        pp.pprint(token_resp.headers)
        pp.pprint(json.loads(token_resp.content.decode('utf-8')))

    auth_token = token_resp.json()

    value = {
        "username": read_data["username"],
        "token": str(auth_token),
        "refresh_token": read_data["refresh_token"],
        "client_id": read_data["client_id"],
        "token_server_uri": read_data["token_server_uri"]
    }
    with open('.test.json', 'w') as f:
        f.write(json.dumps(value))
    print("Refresh Successful...")
    # else:
    #     print("Refresh Unsuccessfull...")

@cli.command()
@click.option('--debug', 'debug', flag_value=True, default=False)
def get_me(debug):
    print('-- me query --')
    query = f"{{ {querys.meQuery} }}"

    with open('.test.json') as f:
        base_data = f.readline()

    bs_data = ''.join(base_data)
    read_data = json.loads(bs_data)

    headers = {
            'content-type': 'application/json',
            'accept': 'application/json',
            'authorization': 'Bearer ' + read_data["token"]
    }

    if debug:
        print("---------------------------------------------------------------------")
        pp.pprint(headers)
        print("---------------------------------------------------------------------")
    
    sb_resp = requests.get(GRAPHQL_URL, headers=headers, params={'query': query})

    print(f"me query response, status code: {sb_resp.status_code}")
    if sb_resp.status_code == 200:
        sb_resp_json = sb_resp.json()
        pp.pprint(sb_resp_json)
    else:
        sb_resp_json = sb_resp.json()
        pp.pprint(sb_resp_json)

@cli.command()
@click.option('--debug', 'debug', flag_value=True, default=False)
def uploadfile(debug):
    with open(CONFIG_FILE_NAME) as f:
        base_data = f.readline()

    bs_data = ''.join(base_data)
    read_data = json.loads(bs_data)

    print("---------------------------------------------------------------------")
    pp.pprint(read_data)
    print("---------------------------------------------------------------------")

    headers = {
            'content-type': 'application/json',
            'accept': 'application/json',
            'authorization': f'Bearer {read_data["token"]}' 
    }

    itemId="5f9982f1d34e9cff790bd2fe"
    filename="sample_error18.png"
    file_path="/Users/hshakya/sample/sample_error18.png"
    # sb_graphql_uri="https://api-beta.staging.sciencebase.gov/graphql"
    # sb_graphql_uri="http://localhost:4000/graphql"

    client.upload_test_with_graphql_upload_session(itemId, filename, file_path, GRAPHQL_URL, headers, debug)

@cli.command()
@click.option('--debug', 'debug', flag_value=True, default=False)
def logout(debug):
    with open(CONFIG_FILE_NAME) as f:
        base_data =  f.readlines()

    bs_data = ''.join(base_data)
    read_data = json.loads(bs_data)
    if debug:
        pp.pprint(read_data)

    os.remove(CONFIG_FILE_NAME)
    click.echo('logging out using %s' % (read_data["username"], ))


def keycloak_login(username, password, debug):
    keycloak_client_config = {
        "realm": "ScienceBase-B",
        "auth-server-url": "https://www.sciencebase.gov/auth",
        "ssl-required": "external",
        "resource": "sb-steve-test-2",
        "public-client": True,
        "confidential-port": 0
    }

    authenticator = auth.DirectAccessAuthenticator(keycloak_client_config)
    authenticator.authenticate(username, password, debug)

    return authenticator


if __name__ == '__main__':
    cli()
