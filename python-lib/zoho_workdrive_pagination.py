from safe_logger import SafeLogger


logger = SafeLogger("zoho pagination", ["password"])
DEFAULT_PAGE_SIZE = 50


class ZohoWorkdrivePagination():
    def __init__(self, batch_size=None):
        self.batch_size = batch_size or DEFAULT_PAGE_SIZE
        self.number_of_tries = None
        self.page_offset = None

    def has_next_page(self, response, items_retrieved):
        if response is None:
            logger.info("ZohoPagination:has_next_page:initialisation")
            self.page_offset = 0
            return True
        if items_retrieved == self.batch_size:
            return True
        return False

    def get_paging_parameters(self, current_params):
        logger.info("ZohoPagination:get_paging_parameters")
        current_params["page[limit]"] = self.batch_size
        current_params["page[offset]"] = self.page_offset
        self.page_offset = self.page_offset + 1
        return current_params
