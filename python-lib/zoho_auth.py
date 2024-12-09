import requests


class ZohoAuth(requests.auth.AuthBase):
    def __init__(self, access_token=None):
        print("ALX:access_token3={}".format(access_token))
        self.access_token = access_token

    def __call__(self, request):
        print("ALX:access_token4={}".format(self.access_token))
        request.headers["Authorization"] = "Zoho-oauthtoken {}".format(
            self.access_token
        )
        request.headers["Accept"] = "application/vnd.api+json"
        # request.headers["Authorization"] = "Bearer {}".format(
        #     self.access_token
        # )
        print("ALX:request.headers={}".format(request.headers))
        return request

# Get Folders List
# https://{zohoapis_domain}/writer/api/v1/folders
