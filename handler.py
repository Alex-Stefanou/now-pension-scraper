import datetime
import os
import pygsheets
import requests
from dotenv import load_dotenv
load_dotenv()

import headers

def run(event, context):
    # Spoof headers to bypass cors
    session = requests.Session()
    session.headers.update(headers.static)
    
    # login to obtain bearer token
    login_payload = {
        'channel': 'web',
        'grant_type': 'password',
        'password': os.environ['NP_PASSWORD'],
        'scope': 'read',
        'username': os.environ['NP_USERNAME']
    }
    login_response = session.post('https://www.nowgatewayx.com//uaa/oauth/token', headers=headers.login, data=login_payload)
    access_token = login_response.json()['access_token']

    # GET /contract api to retrieve pension data
    contract_headers = {
        'authorization': f'Bearer {access_token}',
        'cookie': f'viewed_cookie_policy=; access_token={access_token}'
    }
    contract_response = session.get('https://www.nowgatewayx.com//api/contract', headers=contract_headers)
    contract_response = contract_response.json()[0]['funds']

    pension_value = contract_response['contributions']['value']
    last_updated = datetime.date.fromtimestamp(contract_response['date']/1000.0)
    current_date = datetime.date.today()
    print(f'Your pension value is: £{pension_value}\nThis value was last updated on {last_updated}\nWriting to Google Sheet')

    # Write data to googlesheet
    gc = pygsheets.authorize(service_file='./GCP_service_credentials.json')
    sheet = gc.open_by_key(os.environ['SHEET_ID'])
    sheet1 = sheet[0]
    sheet2 = sheet[1]

    next_row = int(sheet2.cell('B1').value)
    sheet1.update_value(f'A{next_row}', current_date.strftime('%d/%m/%Y'))
    sheet1.update_value(f'B{next_row}', pension_value)
    sheet1.update_value(f'C{next_row}', last_updated.strftime('%d/%m/%Y'))

    next_row += 1
    sheet2.update_value('B1', str(next_row))

    print('Job complete')
    return

if __name__ == "__main__":
    run(0,0)