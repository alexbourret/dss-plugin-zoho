from dataiku.fsprovider import FSProvider
from zoho_client import ZohoClient
from zoho_common import get_zoho_token
import os
import shutil
from io import BytesIO
from safe_logger import SafeLogger
from plugin_details import get_initialization_string


logger = SafeLogger("zoho workdrive", ["password", "zoho_oauth"])


class ZohoWorkDriveFSProvider(FSProvider):
    def __init__(self, root, config, plugin_config):
        """
        :param root: the root path for this provider
        :param config: the dict of the configuration of the object
        :param plugin_config: contains the plugin settings
        """
        logger.info("Starting Zoho Workdrive FS with config={}".format(logger.filter_secrets(config)))
        logger.info("{}".format(get_initialization_string()))
        if len(root) > 0 and root[0] == '/':
            root = root[1:]
        self.root = root
        self.provider_root = "/"
        access_token = get_zoho_token(config)
        self.client = ZohoClient(access_token=access_token, endpoint="workdrive")
        self.folder_id = config.get("folder_id", "me")

    def get_rel_path(self, path):
        if len(path) > 0 and path[0] == '/':
            path = path[1:]
        return path

    def get_lnt_path(self, path):
        if len(path) == 0 or path == '/':
            return '/'
        elts = path.split('/')
        elts = [e for e in elts if len(e) > 0]
        return '/' + '/'.join(elts)

    def get_full_path(self, path):
        path_elts = [self.provider_root, self.get_rel_path(self.root), self.get_rel_path(path)]
        path_elts = [e for e in path_elts if len(e) > 0]
        return os.path.join(*path_elts)

    def close(self):
        """
        Perform any necessary cleanup
        """
        logger.info('close')

    def stat(self, path):
        """
        Get the info about the object at the given path inside the provider's root, or None
        if the object doesn't exist
        """
        full_path = self.get_full_path(path)
        logger.info("stat:path={}, full_path={}".format(path, full_path))
        item = self.client.get_item_from_path(self.folder_id, full_path)
        if not item:
            logger.info("stat:no item found")
            return None
        if is_folder(item):
            return {
                'path': self.get_lnt_path(path),
                'size': item_size(item),
                'lastModified': epoch_last_modified(item),
                'isDirectory': True
            }
        else:
            return {
                'path': self.get_lnt_path(path),
                'size': item_size(item),
                'lastModified': epoch_last_modified(item),
                'isDirectory': False
            }

    def set_last_modified(self, path, last_modified):
        """
        Set the modification time on the object denoted by path. Return False if not possible
        """
        full_path = self.get_full_path(path)
        os.utime(full_path, (os.path.getatime(full_path), last_modified / 1000))
        return True

    def browse(self, path):
        """
        List the file or directory at the given path, and its children (if directory)
        """
        full_path = self.get_full_path(path)
        logger.info("browse:path={}, full_path={}".format(path, full_path))
        item = self.client.get_item_from_path(self.folder_id, full_path)
        if not item:
            logger.info("no item found")
            return {'fullPath': None, 'exists': False}
        if is_folder(item):
            children = []
            for child_item in self.client.get_next_folder_item(item.get("id")):
                child = {
                    'fullPath': path + "" + child_item.get("attributes", {}).get("display_html_name"),
                    'directory': is_folder(child_item),
                    'size': item_size(child_item),
                    'lastModified': epoch_last_modified(item)
                }
                children.append(child)
            return {
                'fullPath': self.get_lnt_path(path),
                'exists': True,
                'directory': True,
                'children': children,
                'lastModified': epoch_last_modified(item)
            }
        else:
            return {
                'fullPath': self.get_lnt_path(path),
                'exists': True,
                'directory': False,
                'size': item_size(item),
                'lastModified': epoch_last_modified(item)
            }

    def enumerate(self, path, first_non_empty):
        """
        Enumerate files recursively from prefix. If first_non_empty, stop at the first non-empty file.

        If the prefix doesn't denote a file or folder, return None
        """
        full_path = self.get_full_path(path)
        logger.info("enumerate:path={}, full_path={}".format(path, full_path))
        item = self.client.get_item_from_path(self.folder_id, full_path)
        if not item:
            return None
        if not is_folder(item):
            return [
                {
                    'path': self.get_lnt_path(path),
                    'size': item_size(item),
                    'lastModified': int(epoch_last_modified(item))
                }
            ]
        else:
            paths = self.get_all_paths(item, "", first_non_empty)
        return paths

    def get_all_paths(self, input_folder_id, folder_path, first_non_empty):
        paths = []
        for item in self.client.get_next_folder_item(input_folder_id.get("id")):
            if is_folder(item):
                paths = paths + self.get_all_paths(item, folder_path + "/" + item.get("attributes", {}).get("display_html_name"), first_non_empty)
            else:
                paths.append(
                    {
                        'path': "{}{}".format(folder_path, self.get_lnt_path(item.get("attributes", {}).get("display_html_name"))),
                        'size': item_size(item),
                        'lastModified': int(epoch_last_modified(item))
                    }
                )
        return paths

    def delete_recursive(self, path):
        """
        Delete recursively from path. Return the number of deleted files (optional)
        """
        full_path = self.get_full_path(path)
        logger.info("delete_recursive:path={}, full_path={}".format(path, full_path))
        item = self.client.get_item_from_path(self.folder_id, full_path)
        if not item:
            return 0
        response = self.client.patch(
            "files",
            json={
                "data": [
                    {
                        "attributes": {
                            "status": "51"
                        },
                        "id": item.get("id"),
                        "type": "files"
                    }
                ]
            }
        )
        logger.info("delete_recursive:response={}".format(response))
        if is_folder(item):
            return 0
        else:
            return 1

    def move(self, from_path, to_path):
        """
        Move a file or folder to a new path inside the provider's root. Return false if the moved file didn't exist
        """
        full_from_path = self.get_full_path(from_path)
        full_to_path = self.get_full_path(to_path)
        logger.info("delete_recursive:from_path={}, full_from_path={}".format(from_path, full_from_path))
        item_to_change = self.client.get_item_from_path(self.folder_id, full_from_path)
        if not item_to_change:
            return False
        from_base_path, from_file_name = os.path.split(full_from_path)
        to_base_path, to_file_name = os.path.split(full_to_path)
        if from_file_name != to_file_name:
            response = self.client.patch(
                "files/{}".format(item_to_change.get("id")),
                json={
                    "data": {
                        "attributes": {
                            "name": "{}".format(to_file_name)
                        },
                        "type": "files"
                    }
                }
            )
        if from_base_path != to_base_path:
            to_base_path_item = self.client.get_item_from_path(self.folder_id, to_base_path)
            response = self.client.patch(
                "files/{}".format(item_to_change.get("id")),
                json={
                    "data": {
                        "attributes": {
                            "parent_id": "{}".format(to_base_path_item.get("id"))
                        },
                        "type": "files"
                    }
                }
            )
            logger.info("move:response={}".format(response))
        return True

    def read(self, path, stream, limit):
        """
        Read the object denoted by path into the stream. Limit is an optional bound on the number of bytes to send
        """
        full_path = self.get_full_path(path)
        logger.info("read:path={}, full_path={}, limit={}".format(path, full_path, limit))
        item = self.client.get_item_from_path(self.folder_id, full_path)
        if not item:
            raise Exception("Path doesn't exist")
        download_url = "https://download.zoho.com/v1/workdrive/download/{}".format(item.get("id"))
        data = self.client.get(None, url=download_url, raw=True)
        file_handle = BytesIO()
        file_handle.write(data.content)
        file_handle.seek(0)
        shutil.copyfileobj(file_handle, stream)

    def write(self, path, stream):
        """
        Write the stream to the object denoted by path into the stream
        """
        full_path = self.get_full_path(path)
        full_path_parent = os.path.dirname(full_path)
        logger.info("write:path={}, full_path={}, full_path_parent={}".format(path, full_path, full_path_parent))
        base_path, file_name = os.path.split(full_path)
        parent_item = self.client.get_item_from_path(self.folder_id, base_path)
        parent_id = parent_item.get("id")
        bio = BytesIO()
        shutil.copyfileobj(stream, bio)
        buffer_size = bio.getbuffer().nbytes
        bio.seek(0)
        logger.info("write:buffer_size={}".format(buffer_size))
        data = bio.read()
        if buffer_size < 1073741824:
            # https://github.com/rclone/rclone/issues/5995
            url = "https://upload.zoho.com/workdrive-api/v1/stream/upload"
            headers = {
                'x-filename': file_name,
                'x-parent_id': parent_id,
                'x-streammode': '1',
                'Content-Type': 'text/plain'
            }
            response = self.client.post(None, url=url, headers=headers, data=data)
        else:
            response = self.client.post("uploadsession/create", params={"size": buffer_size, "file_name": file_name, "parent_id": parent_id})
            logger.info("response={}".format(response))
            upload_id = response.get("upload_id")
            chunk_size = response.get("chunk_size")
            logger.info("write:upload_id={}, chunk_size={}".format(upload_id, chunk_size))
            save_upload_offset = 0
            while save_upload_offset < buffer_size:
                next_save_upload_offset = save_upload_offset + chunk_size
                if next_save_upload_offset >= buffer_size:
                    next_save_upload_offset = buffer_size
                response = self.client.post(
                    None,
                    url="https://upload.zoho.com/workdrive-api/v1/stream/upload",
                    data=data[save_upload_offset:next_save_upload_offset],
                    headers={
                        "upload-id": upload_id,
                        "Content-Range": "bytes {} - {}/{}".format(save_upload_offset, next_save_upload_offset, buffer_size),
                        "x-streammode": "1"
                    },
                    raw=True
                )
                logger.info("upload:response={}".format(response.content))
            response = self.client.post("uploadsession/commit", params={
                    "upload-id": upload_id,
                    "parent_id": parent_id
                }
            )
            logger.info("write:commit:response={}".format(response))


def item_size(item):
    if is_folder(item):
        return 0
    else:
        return int(item.get("attributes", {}).get("storage_info", {}).get("size_in_bytes"))


def epoch_last_modified(item):
    print("ALX:item={}".format(item))
    return int(item.get("attributes", {}).get("modified_time_in_millisecond"))


def is_folder(item):
    return item_type(item) == "folder"


def item_type(item):
    return item.get("attributes", {}).get("type", "")
