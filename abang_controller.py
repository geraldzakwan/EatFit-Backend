import os
import json
import richmenu
import utils
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, PostbackEvent, TextMessage, TextSendMessage, TemplateSendMessage, CarouselTemplate, CarouselColumn, MessageTemplateAction,
    ButtonsTemplate, PostbackTemplateAction
)
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

import postgresql
db = postgresql.PostgreSQL()

line_bot_api = LineBotApi(os.environ['LINE_CHANNEL_ACCESS_TOKEN'])

def set_operational_hour(what_to_set, time):
    db.set_schedule(what_to_set, time)
    if what_to_set == "open_hour":
        res_text = "Jam buka diubah menjadi jam : " + time
    elif what_to_set == "close_hour":
        res_text = "Jam tutup diubah menjadi jam : " + time
    # res_text = str(db.get_schedule()['open_hour'])
    return res_text

def restock(variant, amount):
    type_menu = db.get_type_from_name(variant)

    if(type_menu != 'X'):
        if(db.get_stock(type_menu)['quantity'] == 0):
            notify_restock(variant)
        db.restock(type_menu, amount)
        return 'Restock Indomie ' + str(variant) + ' sebanyak ' + str(amount) + ' bungkus berhasil.'
    else:
        return 'Restock gagal'

def notify_restock(variant):
    type_menu = db.get_type_from_name(variant)
    if(type_menu != 'X'):
        list_unprocessed_orders = db.get_unprocessed_orders(type_menu)
        if (list_unprocessed_orders is not None):
            for user_id in list_unprocessed_orders:
                line_bot_api.push_message(user_id, TextSendMessage(text='Halo, indomie ' + variant + ' sudah restock loh'))

def carousel_restock():
    carousel_template_message = TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url='https://res.cloudinary.com/intern-line/image/upload/v1518103407/indomie-goreng_lzxy9b.jpg',
                    title='Indomie Goreng',
                    text='Indomie yang kuahnya ditirisin',
                    actions=[
                        MessageTemplateAction(
                            label='Tambah',
                            text='Tambah indomie goreng'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://res.cloudinary.com/intern-line/image/upload/v1518103407/indomie-kuah_dhoi8o.jpg',
                    title='Indomie Kuah',
                    text='Indomie yang kuahnya ngk ditirisin',
                    actions=[
                        MessageTemplateAction(
                            label='Tambah',
                            text='Tambah indomie kuah'
                        )
                    ]
                )
            ]
        )
    )
    return carousel_template_message

def is_positive_number(n):
    try:
        n = int(n)

        if(n > 0):
            return True
        else:
            return False
    except ValueError:
        return False


# Immediately send notification to abang whenever a order is created
# Input: u_id --> user who order
def hook_notify_abang(u_id, order_id, menu):
    abang_u_ids = db.get_user_ids('abang')
    for abang_u_id in abang_u_ids:
        u_profile = line_bot_api.get_profile(u_id)
        u_display_name = u_profile.display_name
        u_picture = str(u_profile.picture_url)
        u_picture = u_picture.replace("http", "https")
        print(u_picture)
        bt =    TemplateSendMessage(
                    alt_text= 'Pesanan Baru',
                    template=   ButtonsTemplate(
                                    text= menu, 
                                    title= u_display_name,
                                    thumbnail_image_url= "https://pbs.twimg.com/media/DC17Y33VwAAJOqL.jpg",
                                    image_aspect_ratio="1:1", 
                                    image_size="contain", 
                                    image_background_color="#000000",
                                    actions=[
                                        PostbackTemplateAction(
                                            label= 'Pesanan Diterima',
                                            data = 'accept:' + str(order_id),
                                        ),
                                        PostbackTemplateAction(
                                            label= 'Selesai Dibuat',
                                            data = 'done:' + str(order_id),
                                        )
                                    ]
                                )
                )
        line_bot_api.push_message(to=abang_u_id, messages=[bt])