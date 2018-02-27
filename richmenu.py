import json

import requests


class RichMenuApi(object):

    def __init__(self, channel_access_token):
        self.channel_access_token = channel_access_token

    def get_rich_menu(self, rich_menu_id):
        headers = {
            'authorization': 'Bearer ' + self.channel_access_token
        }
        url = 'https://api.line.me/v2/bot/richmenu/{rich_menu_id}'.format(rich_menu_id=rich_menu_id)
        r = requests.get(url, headers=headers)
        response = json.loads(r.text)
        return r.status_code, response

    def create_rich_menu(self, rich_menu):
        headers = {
            'authorization': 'Bearer ' + self.channel_access_token,
            'content-type': 'application/json'
        }
        url = 'https://api.line.me/v2/bot/richmenu'
        r = requests.post(url, data=json.dumps(rich_menu), headers=headers)
        response = json.loads(r.text)
        return r.status_code, response

    def delete_rich_menu(self, rich_menu_id):
        headers = {
            'authorization': 'Bearer ' + self.channel_access_token
        }
        url = 'https://api.line.me/v2/bot/richmenu/{rich_menu_id}'.format(rich_menu_id=rich_menu_id)
        r = requests.delete(url, headers=headers)
        response = json.loads(r.text)
        return r.status_code, response

    def get_rich_menu_id_of_user(self, user_id):
        headers = {
            'authorization': 'Bearer ' + self.channel_access_token
        }
        url = 'https://api.line.me/v2/bot/user/{user_id}/richmenu'.format(user_id=user_id)
        r = requests.get(url, headers=headers)
        response = json.loads(r.text)
        return r.status_code, response

    def link_rich_menu_to_user(self, user_id, rich_menu_id):
        headers = {
            'authorization': 'Bearer ' + self.channel_access_token
        }
        url = 'https://api.line.me/v2/bot/user/{user_id}/richmenu/{rich_menu_id}'.format(user_id=user_id, rich_menu_id=rich_menu_id)
        r = requests.post(url, headers=headers)
        response = json.loads(r.text)
        return r.status_code, response

    def unlink_rich_menu_from_user(self, user_id):
        headers = {
            'authorization': 'Bearer ' + self.channel_access_token
        }
        url = 'https://api.line.me/v2/bot/user/{user_id}/richmenu'.format(user_id=user_id)
        r = requests.delete(url, headers=headers)
        response = json.loads(r.text)
        return r.status_code, response

    def upload_rich_menu_image(self, rich_menu_id, image_path):
        if image_path.lower().endswith('png'):
            content_type = 'image/png'
        elif image_path.lower().endswith('jpg') or image_path.lower().endswith('jpeg'):
            content_type = 'image/jpeg'
        else:
            return None, None

        headers = {
            'authorization': 'Bearer ' + self.channel_access_token,
            'content-type': content_type
        }
        url = 'https://api.line.me/v2/bot/richmenu/{rich_menu_id}/content'.format(rich_menu_id=rich_menu_id)
        r = requests.post(url, data=open(image_path, 'rb'), headers=headers)
        response = json.loads(r.text)
        return r.status_code, response

    def get_rich_menu_list(self):
        headers = {
            'authorization': 'Bearer ' + self.channel_access_token
        }
        url = 'https://api.line.me/v2/bot/richmenu/list'
        r = requests.get(url, headers=headers)
        response = json.loads(r.text)
        return r.status_code, response
