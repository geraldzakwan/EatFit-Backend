import os
import json

from dotenv import load_dotenv, find_dotenv
from postgresql import PostgreSQL
from richmenu import RichMenuApi


load_dotenv(find_dotenv(), override=True)

channel_access_token = os.environ['LINE_CHANNEL_ACCESS_TOKEN']

db = PostgreSQL()

rich_menu_api = RichMenuApi(channel_access_token)
rich_menus = {}

def c5_rich_menu_json():
    json_text = '{ "size":{"width":2500, "height":1686}, "selected":false, "name":"Dashboard", "chatBarText":"Dashboard", "areas":[{ "bounds":{ "x":0, "y":0, "width":2500, "height":1686}, "action":{"type":"uri", "label":"View dashboard", "uri":"https://sarip-bot.herokuapp.com/leaderboard"}}]}'
    return json.loads(json_text)

def b4_rich_menu_json():
    json_text = '{ "size":{"width":2500, "height":1686}, "selected":false, "name":"Atur Jam", "chatBarText":"Atur Jam", "areas":[{ "bounds":{ "x":0, "y":0, "width":1250, "height":1686}, "action":{"type":"datetimepicker","label":"Select time","data":"open_hour","mode":"time","initial":"00:00","max":"23:59","min":"00:00"}}, { "bounds":{ "x":1250, "y":0, "width":1250, "height":1686}, "action":{"type":"datetimepicker","label":"select close time","data":"close_hour","mode":"time","initial":"00:00","max":"23:59","min":"00:00"}}]}'
    return json.loads(json_text)

def track_order_rich_menu():
    return {
        "size": {
            "width": 2500,
            "height": 1686
        },
        "selected": True,
        "name": "Track Order",
        "chatBarText": "Track Order",
        "areas": [
            {
                "bounds": {
                    "x": 0,
                    "y": 0,
                    "width": 2500,
                    "height": 1686
                },
                "action": {
                    "type": "message",
                    "text": "Bang, saya urutan ke berapa?"
                }
            }
        ]
    }

def delete_all_rich_menu():
    richmenu_obj = RichMenuApi(channel_access_token)

    # Get all rich menu attached
    response = richmenu_obj.get_rich_menu_list()
    list_to_be_deleted = []
    for ind_rich_menu in response[1]['richmenus']:
        list_to_be_deleted.append(ind_rich_menu['richMenuId'])

    # Delete all
    for richMenuId in list_to_be_deleted:
        richmenu_obj.delete_rich_menu(richMenuId)

    return list_to_be_deleted

def b4_rich_menu_wrapper():
    richmenu_obj = RichMenuApi(channel_access_token)

    # Create rich menu obj and get id
    response = richmenu_obj.create_rich_menu(b4_rich_menu_json())
    # print(response)
    richmenu_id = response[1]['richMenuId']

    # Upload image
    # image_path = "https://res.cloudinary.com/intern-line/image/upload/v1518054234/go_to_admin_dashboard_pa2pzv.png"
    # image_path = "D:/LINE Internship/b4_richmenu.png"
    image_path = "richmenu_image/b4_richmenu.png"
    response = richmenu_obj.upload_rich_menu_image(richmenu_id, image_path)
    # print('Upload image succesful')
    # print(response)

    # Link to user
    # response = richmenu_obj.link_rich_menu_to_user(utils.user_ids['abang'][-1], richmenu_id)
    abang_user_ids = db.get_user_ids('abang')
    for user_id in abang_user_ids:
        response = richmenu_obj.link_rich_menu_to_user(user_id, richmenu_id)
        # print(response)

def c5_rich_menu_wrapper():
    richmenu_obj = RichMenuApi(channel_access_token)

    # Create rich menu obj and get id
    response = richmenu_obj.create_rich_menu(c5_rich_menu_json())
    # print(response)
    richmenu_id = response[1]['richMenuId']

    # Upload image
    # image_path = "https://res.cloudinary.com/intern-line/image/upload/v1518054234/go_to_admin_dashboard_pa2pzv.png"
    # image_path = "D:/LINE Internship/c5_richmenu.png"
    image_path = "richmenu_image/c5_richmenu.png"
    response = richmenu_obj.upload_rich_menu_image(richmenu_id, image_path)
    # print('Upload image succesful')
    # print(response)

    # Link to user
    # response = richmenu_obj.link_rich_menu_to_user(utils.user_ids['hr'][-1], richmenu_id)
    hr_user_ids = db.get_user_ids('hr')
    for user_id in hr_user_ids:
        response = richmenu_obj.link_rich_menu_to_user(user_id, richmenu_id)
        # print(response)

def create_track_order_rich_menu():
    response = rich_menu_api.create_rich_menu(track_order_rich_menu())
    rich_menu_id = response[1]['richMenuId']
    rich_menus['track_order'] = rich_menu_id
    image_path = 'richmenu_image/track_order.jpeg'
    rich_menu_api.upload_rich_menu_image(rich_menu_id, image_path)

def link_track_order_rich_menu(user_id):
    rich_menu_api.link_rich_menu_to_user(user_id, rich_menus['track_order'])

def unlink_rich_menu(user_id):
    rich_menu_api.unlink_rich_menu_from_user(user_id)

def initiate_all_rich_menu():
    b4_rich_menu_wrapper()
    c5_rich_menu_wrapper()
    create_track_order_rich_menu()
