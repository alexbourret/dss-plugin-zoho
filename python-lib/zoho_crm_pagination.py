from safe_logger import SafeLogger


logger = SafeLogger("zoho pagination", ["password"])
DEFAULT_PAGE_SIZE = 10000


class ZohoCRMPagination():
    '''
    "info": {
        "per_page": 200,
        "next_page_token": null,
        "count": 10,
        "sort_by": "id",
        "page": 1,
        "previous_page_token": null,
        "page_token_expiry": null,
        "sort_order": "desc",
        "more_records": false
    }
    '''
    def __init__(self, batch_size=None):
        self.batch_size = batch_size or DEFAULT_PAGE_SIZE
        self.number_of_tries = None
        self.page_offset = None
        self.next_page_token = None
        self.page = 0

    def has_next_page(self, response, items_retrieved):
        if response is None:
            logger.info("ZohoPagination:has_next_page:initialisation")
            self.page_offset = 0
            return True
        json_response = response.json()
        self.next_page_token = json_response.get("info", {}).get("next_page_token", None)
        page = json_response.get("info", {}).get("page")
        if page:
            self.page = int(page)
        return json_response.get("info", {}).get("more_records", False)

    def get_paging_parameters(self, current_params):
        logger.info("ZohoPagination:get_paging_parameters")
        # params = {"pageToken": "{}".format(self.next_page_token)}
        next_page = None
        if self.page and isinstance(self.page, int):
            next_page = self.page + 1
        if next_page:
            current_params["page"] = next_page
        return current_params
