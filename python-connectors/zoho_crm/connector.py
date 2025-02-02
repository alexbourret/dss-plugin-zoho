# This file is the actual code for the custom Python dataset zoho_crm

# import the base class for the custom dataset
from six.moves import xrange
from dataiku.connector import Connector
from safe_logger import SafeLogger
from plugin_details import get_initialization_string
from zoho_client import ZohoClient
from zoho_common import get_zoho_token, RecordsLimit


logger = SafeLogger("zoho CRM", ["password", "zoho_oauth"])

"""
A custom Python dataset is a subclass of Connector.

The parameters it expects and some flags to control its handling by DSS are
specified in the connector.json file.

Note: the name of the class itself is not relevant.
"""


class ZohoCRMConnector(Connector):

    def __init__(self, config, plugin_config):
        """
        The configuration parameters set up by the user in the settings tab of the
        dataset are passed as a json object 'config' to the constructor.
        The static configuration parameters set up by the developer in the optional
        file settings.json at the root of the plugin directory are passed as a json
        object 'plugin_config' to the constructor
        """
        Connector.__init__(self, config, plugin_config)  # pass the parameters to the base class
        logger.info("Starting Zoho Workdrive FS with config={}".format(logger.filter_secrets(config)))
        logger.info("{}".format(get_initialization_string()))
        # perform some more initialization
        self.table = self.config.get("table", "users")
        access_token = get_zoho_token(config)
        self.client = ZohoClient(access_token=access_token, endpoint="crm")

    def get_read_schema(self):
        """
        Returns the schema that this connector generates when returning rows.

        The returned schema may be None if the schema is not known in advance.
        In that case, the dataset schema will be infered from the first rows.

        If you do provide a schema here, all columns defined in the schema
        will always be present in the output (with None value),
        even if you don't provide a value in generate_rows

        The schema must be a dict, with a single key: "columns", containing an array of
        {'name':name, 'type' : type}.

        Example:
            return {"columns" : [ {"name": "col1", "type" : "string"}, {"name" :"col2", "type" : "float"}]}

        Supported types are: string, int, bigint, float, double, date, boolean
        """

        # In this example, we don't specify a schema here, so DSS will infer the schema
        # from the columns actually returned by the generate_rows method
        return None

    def generate_rows(self, dataset_schema=None, dataset_partitioning=None,
                      partition_id=None, records_limit=-1):
        """
        The main reading method.

        Returns a generator over the rows of the dataset (or partition)
        Each yielded row must be a dictionary, indexed by column name.

        The dataset schema and partitioning are given for information purpose.
        """
        limit = RecordsLimit(records_limit)
        endpoints = {
            "contacts": {"endpoint": "Contacts", "data_path": ["data"], "params": {"fields": "Last_Name,Email"}},
            "apis": {"endpoint": "__apis", "data_path": ["__apis"], "params": {}},
            "users": {"endpoint": "users", "data_path": ["users"], "params": {}},
            "events": {"endpoint": "Events", "data_path": ["data"], "params": {"fields": "Owner,Venue,Description"}}
        }
        endpoint = endpoints.get(self.table, {})
        for item in self.client.client.get_next_row(endpoint.get("endpoint"), data_path=endpoint.get("data_path"), params=endpoint.get("params")):
            yield item
            if limit.is_reached():
                break

    def get_writer(self, dataset_schema=None, dataset_partitioning=None,
                   partition_id=None):
        """
        Returns a writer object to write in the dataset (or in a partition).

        The dataset_schema given here will match the the rows given to the writer below.

        Note: the writer is responsible for clearing the partition, if relevant.
        """
        raise NotImplementedError

    def get_partitioning(self):
        """
        Return the partitioning schema that the connector defines.
        """
        raise NotImplementedError

    def list_partitions(self, partitioning):
        """Return the list of partitions for the partitioning scheme
        passed as parameter"""
        return []

    def partition_exists(self, partitioning, partition_id):
        """Return whether the partition passed as parameter exists

        Implementation is only required if the corresponding flag is set to True
        in the connector definition
        """
        raise NotImplementedError

    def get_records_count(self, partitioning=None, partition_id=None):
        """
        Returns the count of records for the dataset (or a partition).

        Implementation is only required if the corresponding flag is set to True
        in the connector definition
        """
        raise NotImplementedError


class CustomDatasetWriter(object):
    def __init__(self):
        pass

    def write_row(self, row):
        """
        Row is a tuple with N + 1 elements matching the schema passed to get_writer.
        The last element is a dict of columns not found in the schema
        """
        raise NotImplementedError

    def close(self):
        pass
