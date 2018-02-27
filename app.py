import os
import sys
import abang_controller
import richmenu_manager

from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from flask import Flask, request, abort, session, redirect, render_template
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, PostbackEvent, TextMessage, TextSendMessage
)

from urllib import parse, request as req
from richmenu import RichMenuApi
from postgresql import PostgreSQL
import jwt, json


load_dotenv(find_dotenv(), override=True)

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

web_channel_id = os.getenv('LINE_WEB_CHANNEL_ID', None)
web_channel_secret = os.getenv('LINE_WEB_CHANNEL_SECRET', None)
auth_redir = os.getenv('AUTH_REDIRECT', None)

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)
if web_channel_id is None:
    print('Specify LINE_WEB_CHANNEL_ID as environment variable.')
    sys.exit(1)
if web_channel_secret is None:
    print('Specify LINE_WEB_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if auth_redir is None:
    print('Specify AUTH_REDIRECT as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
rich_menu_api = RichMenuApi(channel_access_token)
handler = WebhookHandler(channel_secret)
db = PostgreSQL()

message_history = ["dummy"]

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@app.route('/leaderboard')
def home():
	if not session.get('logged_in'):
		return redirect("https://access.line.me/oauth2/v2.1/authorize?response_type=code&client_id=" + web_channel_id + "&redirect_uri=" + auth_redir + "&state=12345abcde&scope=openid%20profile", code=302)
	else:
		datas = {}
		successful_orders = db.get_daily_successful_orders(datetime.today().date())
		unsuccessful_orders = db.get_daily_unsuccessful_orders(datetime.today().date())
		leaderboard_ids = db.get_orders_leaderboard()
		leaderboard_names = []
		for leaderboard_id in leaderboard_ids:
			try:
				profile = line_bot_api.get_profile(leaderboard_id[0])
				leaderboard_names.append((profile.display_name, leaderboard_id[1]))
			except:
				leaderboard_names.append((leaderboard_id[0], leaderboard_id[1]))
		datas['so'] = successful_orders
		datas['uo'] = unsuccessful_orders
		datas['lb'] = leaderboard_names
		return render_template("leaderboard.html", data=datas)
    
@app.route('/auth')
def auth():
	data_dict = {}
	data_dict['Content-Type'] = "application/x-www-form-urlencoded"
	data_dict['grant_type'] = "authorization_code"
	data_dict['code'] = request.args.get("code")
	data_dict['redirect_uri'] = auth_redir
	data_dict['client_id'] = web_channel_id
	data_dict['client_secret'] = web_channel_secret
	data = parse.urlencode(data_dict).encode()
	req_data =  req.Request("https://api.line.me/oauth2/v2.1/token", data=data)
	resp = req.urlopen(req_data)
	resp_data = json.loads(resp.read().decode('utf-8'))
	decoded_id_token = jwt.decode(resp_data['id_token'],
								  web_channel_secret,
								  audience=web_channel_id,
								  issuer='https://access.line.me',
								  algorithms=['HS256'])
	if (db.is_hr(decoded_id_token['sub'])):
		session['logged_in'] = True
	return redirect('/leaderboard')

@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    global message_history

    in_text = event.message.text.lower()

    user = db.get_user(event.source.user_id)

    if user is None:
        user_id = event.source.user_id
        reply_token = event.reply_token
        if event.message.text.lower() == 'pesan indomie goreng':
            if is_open(reply_token) and not has_order(user_id, reply_token) and stock_available('G', user_id,
                                                                                                reply_token):
                new_order_id = db.insert_order(user_id, 'G', 0)
                abang_controller.hook_notify_abang(user_id, new_order_id, "Indomie Goreng") # Send Notification to Abang
                richmenu_manager.link_track_order_rich_menu(user_id)
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text='OK, tunggu abangnya ngecek ya')
                )
        elif event.message.text.lower() == 'pesan indomie rebus':
            if is_open(reply_token) and not has_order(user_id, reply_token) and stock_available('R', user_id,
                                                                                                reply_token):
                new_order_id = db.insert_order(user_id, 'R', 0)
                abang_controller.hook_notify_abang(user_id, new_order_id, "Indomie Rebus") # Send Notification to Abang
                richmenu_manager.link_track_order_rich_menu(user_id)
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text='OK, tunggu abangnya ngecek ya')
                )

    if ('bantuan' in in_text):
        res_text = "1. Ketik 'daftar sebagai abang' untuk menjadi abang atau 'resign sebagai abang' untuk resign sebagai abang" + "\n" + "2. Ketik 'daftar sebagai hr' untuk menjadi HR atau 'resign sebagai hr' untuk resign sebagai hr" + "\n" + "3. Untuk restock sebagai abang, ketik : 'tambah stok' kemudian ikuti proses selanjutnya"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=res_text)
        )
    elif('tambah stok' in in_text):
        if(db.is_abang(event.source.user_id)):
            line_bot_api.reply_message(
                event.reply_token,
                abang_controller.carousel_restock()
            )
        else:
            res_text = "Kamu bukan abang, ngk bisa restock hehe"
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=res_text)
            )
    elif('tambah indomie' in in_text):
        if(db.is_abang(event.source.user_id)):
            res_text = "Nambah berapa ni?"
            message_history.append(in_text)
        else:
            res_text = "Kamu bukan abang, ngk bisa restock hehe"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=res_text)
        )
    elif('tambah indomie' in message_history[-1] and abang_controller.is_positive_number(in_text)):
        if(db.is_abang(event.source.user_id)):
            variant = message_history[-1].split(' ')[2]
            app.logger.info("Varian  : " + variant)
            res_text = abang_controller.restock(variant, int(in_text))
            message_history = ["dummy"]
        else:
            res_text = "Kamu bukan abang, ngk bisa restock hehe"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=res_text)
        )
    elif('tambah indomie' in message_history[-1] and not abang_controller.is_positive_number(in_text)):
        if(db.is_abang(event.source.user_id)):
            res_text = "Angkanya harus bulet positif ya bro haha"
        else:
            res_text = "Kamu bukan abang, ngk bisa restock hehe"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=res_text)
        )
    elif('urutan ke berapa?' in in_text):
        u_id = event.source.user_id
        user_order_position = get_user_order_position(u_id)
        if user_order_position is not None:
            queue = user_order_position - 1
            if(queue>0):
                res_text = "Masih ada " + str(queue) + " lagi, sebentar ya"
            else:
                res_text = "Kamu yang pertama bro"
        else:
            res_text = "Kamu belum mesen bro"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=res_text)
        )
    elif('test abe' in in_text):
        abang_controller.hook_notify_abang(event.source.user_id)
    elif(in_text == 'daftar sebagai abang'):
        u_id = event.source.user_id
        if(db.is_abang(u_id)):
            res_text = 'Kamu sudah jadi abang bro'
        elif(db.is_hr(u_id)):
            res_text = 'Kamu sudah jadi hr bro, resign dulu'
        else:
            db.add_abang_id(event.source.user_id)
            res_text = "Selamat sudah jadi abang indomie!"
            richmenu_manager.b4_rich_menu_wrapper()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=res_text)
        )
    elif(in_text == 'daftar sebagai hr'):
        u_id = event.source.user_id
        if(db.is_abang(u_id)):
            res_text = 'Kamu sudah jadi abang bro, resign dulu'
        elif(db.is_hr(u_id)):
            res_text = 'Kamu sudah jadi hr bro'
        else:
            db.add_hr_id(event.source.user_id)
            res_text = "Selamat sudah jadi hr!"
            richmenu_manager.c5_rich_menu_wrapper()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=res_text)
        )
    elif(in_text == 'resign sebagai abang'):
        u_id = event.source.user_id
        if(not db.is_abang(u_id)):
            res_text = 'Kamu bukan abang bro'
        else:
            db.del_abang_id(event.source.user_id)
            res_text = "Kamu sudah resign sebagai abang!"
            richmenu_manager.unlink_rich_menu(event.source.user_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=res_text)
        )
    elif(in_text == 'resign sebagai hr'):
        u_id = event.source.user_id
        if(not db.is_hr(u_id)):
            res_text = 'Kamu bukan hr bro'
        else:
            db.del_hr_id(event.source.user_id)
            res_text = "Kamu sudah resign sebagai hr!"
            richmenu_manager.unlink_rich_menu(event.source.user_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=res_text)
        )
    elif('pesanan' in in_text and 'diterima' in in_text):
        pass
    elif('pesanan' in in_text and 'selesai' in in_text):
        pass
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='Maaf saya tidak mengerti pertanyaan kamu, hehe')
        )

@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data
    if("accept" in data):
        order_id = data.split(":")[1]
        order = db.get_order(order_id)

        u_id = order['user_id']
        u_profile = line_bot_api.get_profile(u_id)
        u_display_name = u_profile.display_name

        if(order['status']==0):
            db.update_status_order(order_id, 1)

            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='Pesanan ' + u_display_name + ' diterima')
            )

            line_bot_api.push_message(to=u_id, messages=[TextSendMessage(text='Pesanan sudah diterima abang, sabar yaa')])

            app.logger.info("Order accepted")
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='Pesanan ' + u_display_name + ' gagal diterima')
            )
    elif("done" in data):
        order_id = data.split(":")[1]
        order = db.get_order(order_id)

        u_id = order['user_id']
        u_profile = line_bot_api.get_profile(u_id)
        u_display_name = u_profile.display_name

        if(order['status']==1):
            db.update_status_order(order_id, 2)
            
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='Pesanan ' + u_display_name + ' selesai')
            )

            hook_notify_cust(u_id)
            richmenu_manager.unlink_rich_menu(u_id)
            
            app.logger.info("Order done")
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='Pesanan ' + u_display_name + ' gagal diselesaikan')
            )
    else:
        time = event.postback.params["time"]
        what_to_set = event.postback.data
        res_text = abang_controller.set_operational_hour(what_to_set, time)

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=res_text))

# Immediately send notification to customer whenever his/her order is finished
# Input: u_id --> user who order
def hook_notify_cust(u_id):
    line_bot_api.push_message(to=u_id, messages=[TextSendMessage(text='Pesanan selesai dibuat')])
    
def is_open(reply_token):
    schedule = db.get_schedule()
    open_hour = datetime.strptime(schedule['open_hour'], '%H:%M').time()
    close_hour = datetime.strptime(schedule['close_hour'], '%H:%M').time()
    now = datetime.now().time()
    if now >= open_hour and now <= close_hour:
        return True
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(text='Yah lagi gak melayani, lain kali ya :(')
    )
    return False


def has_order(user_id, reply_token):
    order = db.get_order_order(user_id)
    if order is not None:
        if order - 1 == 0:
            reply_text = 'Sabar bro, yang tadi belum jadi, gak ada antrian lagi kok'
        else:
            reply_text = 'Sabar bro, yang tadi belum jadi, masih ada {} lagi'.format(order - 1)
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=reply_text)
        )
        return True
    return False

def get_user_order_position(user_id):
    order_num = db.get_order_order(user_id)
    if order_num is not None:
        return order_num
    else:
        return None

def stock_available(type_menu, user_id, reply_token):
    stock = db.get_stock(type_menu)
    if stock['quantity'] > 0:
        return True

    if not db.has_unprocessed_order(user_id, type_menu):
        db.insert_order(user_id, type_menu, -1)

    if type_menu == 'G':
        reply_text = 'Yah stok Indomie gorengnya lagi kosong :('
    elif type_menu == 'R':
        reply_text = 'Yah stok Indomie rebusnya lagi kosong :('
    else:
        reply_text = 'Yah stoknya lagi kosong :('
    line_bot_api.reply_message(
        reply_token,
        TextSendMessage(text=reply_text)
    )
    line_bot_api.push_message(
        user_id,
        TextSendMessage(text='Nanti dikasih tau kl udah restock kok!')
    )
    return False

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    try:
        port = int(os.environ['PORT'])
    except KeyError:
        print('Specify PORT as environment variable.')
        sys.exit(1)
    except TypeError:
        print('PORT must be an integer.')
        sys.exit(1)

    richmenu_manager.delete_all_rich_menu()
    richmenu_manager.initiate_all_rich_menu()

    app.run(host='0.0.0.0', port=port, debug=False)
