import json
import logging
import re
import requests


class MastodonAPI:

    def __init__(self, instance_url, access_token):

        self.is_bootstrapped = False

        # Basic validation of URI schema.
        m = re.match('https?://.*', instance_url)
        if m:
            self.instance_url = m.group()
        else:
            self._is_valid = False
            self.instance_url = ""

        # Trivial validation that instance_name is at least something that
        # COULD be a valid domain-name, which is what an instance_name is.

        self.instance_name = ""
        
        if self.instance_url:
            instance_name = self.instance_url.split("://")[1]
            m = re.match('.*..*', instance_name)
            
            if m:
                self.instance_name = m.group()
            else:
                self._is_valid = False

        self.session = requests.Session()
        self.session.headers = {"Authorization": f"Bearer {access_token}"}
        self.account_id = None

    def is_valid(self):

        if self._is_valid:
            return True

        return False

    def validate_credentials(self) -> bool:

        API_ENDPOINT = f"/api/v1/accounts/verify_credentials"

        response = self.session.get(self.instance_url + API_ENDPOINT)

        try:
            jd = json.loads(response.text)
        except ValueError:
            logging.debug(f'JSON loads failed')
            return False

        if response.status_code == 200:
            logging.debug(f'Credentials validated successfully with returncode \
                {response.status_code}')
            self.account_id = jd['id']
            self.is_bootstrapped = True

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
