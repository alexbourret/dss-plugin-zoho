def get_zoho_token(config):
    # auth_type = config.get("auth_type", "sso")
    return config.get("zoho_oauth", {}).get("zoho_oauth")


class RecordsLimit():
    def __init__(self, records_limit=-1):
        self.has_no_limit = (records_limit == -1)
        self.records_limit = records_limit
        self.counter = 0

    def is_reached(self):
        if self.has_no_limit:
            return False
        self.counter += 1
        return self.counter > self.records_limit
