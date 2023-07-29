import json
import logging

from curator.masto_api.api import MastodonAPI


class TimelinesAPI(MastodonAPI):

    def __init__(self, instance_url, access_token):
        super().__init__(instance_url, access_token)

    def list_exist(self, list_name) -> bool:

        API_ENDPOINT = f"/api/v1/lists"

        response = self.session.get(self.instance_url + API_ENDPOINT)

        jd = json.loads(response.text)

        for named_list in jd:

            if list_name in named_list['title']:
                return True
        
        return False

    def create_list(self, list_name) -> bool:

        API_ENDPOINT = f"/api/v1/lists"

        data = {'title': list_name}
        logging.debug(f'Attempting to create list: {list_name}')
        response = self.session.post(self.instance_url + API_ENDPOINT, json=data)

        if not response.status_code == 200:
            logging.debug(f'Response from server: {response.text}')
            return False

        return True

    def get_list(self, list_name) -> dict:

        if not self.list_exist(list_name):
            self.create_list(list_name)

        API_ENDPOINT = f"/api/v1/lists"

        response = self.session.get(self.instance_url + API_ENDPOINT)

        if response.status_code == 200:
            jd = json.loads(response.text)

            for li in jd:

                if list_name in li['title']:
                    return li

        return {}

    def add_accounts_to_list(self, accounts: list, list_name: str) -> bool:

        # 1. First check if the list already exist

        if not self.list_exist(list_name):
            if not self.create_list(list_name):
                logging.error(f'Could NOT create list: {list_name}')
                return False

        # 2. Add all accounts to list.
        named_list = self.get_list(list_name)
        account_ids_to_add = list(set([str(account['id']) for account in accounts]))

        API_ENDPOINT = f'/api/v1/lists/{named_list["id"]}/accounts'

        data = {'account_ids': account_ids_to_add}
        
        response = self.session.post(self.instance_url + API_ENDPOINT, json=data)

        if response.status_code == 200:
            return True

        return False
