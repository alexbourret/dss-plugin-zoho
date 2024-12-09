from zoho_auth import ZohoAuth
from zoho_workdrive_pagination import ZohoWorkdrivePagination
from zoho_crm_pagination import ZohoCRMPagination
from api_client import APIClient


class ZohoClient():
    def __init__(self, access_token=None, endpoint=None):
        endpoint = endpoint or "workdrive"
        if endpoint == "workdrive":
            pagination = ZohoWorkdrivePagination()
            server_url = "https://www.zohoapis.com/workdrive/api/v1"
        else:
            pagination = ZohoCRMPagination()
            server_url = "https://www.zohoapis.com/crm/v7"
        self.client = APIClient(
            server_url=server_url,
            auth=ZohoAuth(access_token=access_token),
            pagination=pagination,
            max_number_of_retries=1
        )

    def get_item_from_path(self, root_folder_id, path):
        if path == "/":
            path = ""
            return {"id": root_folder_id, "attributes": {"type": "folder"}}
        if path.endswith("/"):
            path = path[:-1]
        path_tokens = path.split("/")
        path_tokens.pop(0)

        next_item_id = root_folder_id
        next_item = {}
        countdown = len(path_tokens)
        for path_token in path_tokens:
            countdown -= 1
            next_item = self.find_folder(next_item_id, path_token, can_be_file=(countdown == 0))
            next_item_id = next_item.get("id")
        return next_item

    def get_next_folder_item_from_path(self, root_folder_id, path):
        path_tokens = path.strip("/").split("/")
        next_folder_id = root_folder_id
        countdown = len(path_tokens)
        for path_token in path_tokens:
            countdown -= 1
            if path_token:
                next_folder = self.find_folder(next_folder_id, path_token, can_be_file=(countdown == 0))
                next_folder_id = next_folder.get("id")
            else:
                for row in self.get_next_folder_item(next_folder_id):
                    yield row

    def find_folder(self, root_folder_id, folder_name, can_be_file=False):
        for next_item in self.get_next_folder_item(root_folder_id):
            if not folder_name:
                # Probably asking the root folder
                return next_item
            item_type = next_item.get("attributes", {}).get("type")
            item_name = next_item.get("attributes", {}).get("display_html_name")
            if (item_type == "folder" or can_be_file) and item_name == folder_name:
                return next_item
        raise Exception("Path element '{}' not found".format(folder_name))

    def get_next_folder_item(self, folder_id):
        endpoint = "files/{}/files".format(folder_id)
        for row in self.client.get_next_row(endpoint, data_path=["data"]):
            yield row

    def get_next_item(self, endpoint, ):
        for page in self.get_next_page(endpoint):
            for item in page.get("data", []):
                yield item

    def get_next_page(self, endpoint):
        response = self.get(endpoint)
        return response

    def get(self, endpoint, url=None, raw=False):
        response = self.client.get(endpoint, url=url, raw=raw)
        return response

    def post(self, endpoint, url=None, raw=False, params=None, data=None, json=None, headers=None):
        response = self.client.post(endpoint, url=url, raw=raw, params=params, data=data, json=json, headers=headers)
        return response

    def patch(self, endpoint, url=None, raw=False, params=None, data=None, json=None, headers=None):
        response = self.client.patch(endpoint, url=url, raw=raw, params=params, data=data, json=json, headers=headers)
        return response
