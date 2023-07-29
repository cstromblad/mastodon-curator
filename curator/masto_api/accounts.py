import json
import logging

from curator.masto_api.api import MastodonAPI


class AccountsAPI(MastodonAPI):

    def __init__(self, instance_url, access_token):
        super().__init__(instance_url, access_token)

    def follow(self, account_id) -> bool:

        API_ENDPOINT = f"/api/v1/accounts/{account_id}/follow"
        
        response = self.session.post(self.instance_url + API_ENDPOINT)

        if response.status_code == 200:
            logging.debug(f'Followed {account_id} successfully!')

            return True
        else:
            logging.debug(f'Account NOT followed. Reason: {response.text}')

        return False

    def unfollow(self, account_id) -> dict:

        API_ENDPOINT = f"/api/v1/accounts/{account_id}/unfollow"
        
        response = self.session.post(self.instance_url + API_ENDPOINT)

        if response.status_code == 200:
            logging.debug(f'Unfollowed {account_id} successfully!')

            return json.loads(response.text)
        else:
            logging.debug(f'Account NOT unfollowed. Reason: {response.text}')

        return {}
