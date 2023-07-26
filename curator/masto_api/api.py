import json
import logging
import requests


class MastodonAPI:

    def __init__(self, instance_url, access_token):

        self.instance_url = instance_url
        self.session = requests.Session()
        self.session.headers = {"Authorization": f"Bearer {access_token}"}
        self.account_id = None

    def validate_credentials(self) -> bool:

        API_ENDPOINT = f"/api/v1/accounts/verify_credentials"

        response = self.session.get(self.instance_url + API_ENDPOINT)

        try:
            jd = json.loads(response.text)
        except ValueError:
            logging.debug(f'JSON loads failed')
            return False

        if response.status_code == 200:
            logging.debug(f'Credentials validated successfully with return code {response.status_code}')
            self.account = jd['id']
            return True

        return False

    def follow_account(self, account_id) -> dict:

        API_ENDPOINT = f"/api/v1/accounts/{account_id}/follow"
        
        response = self.session.post(self.instance_url + API_ENDPOINT)

        if response.status_code == 200:
            logging.debug(f'Followed {account_id} successfully!')

            return json.loads(response.text)
        else:
            logging.debug(f'Account NOT followed. Reason: {response.text}')

        return {}

    def unfollow_account(self, account_id) -> dict:

        API_ENDPOINT = f"/api/v1/accounts/{account_id}/unfollow"
        
        response = self.session.post(self.instance_url + API_ENDPOINT)

        if response.status_code == 200:
            logging.debug(f'Unfollowed {account_id} successfully!')

            return json.loads(response.text)
        else:
            logging.debug(f'Account NOT unfollowed. Reason: {response.text}')

        return {}
