from flask import Flask, request, abort

import tempfile
import os
import sys
import errno


from features.CarAnalytics import LicencePlate

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageTemplateAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URITemplateAction,
    PostbackTemplateAction, DatetimePickerTemplateAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent
)

import ptt

app = Flask(__name__)

latest_image_path = ""
#zincBot
#line_bot_api = LineBotApi('GnZxefH4pGG1ubbStIfsAzQ4YLvReiC3reZWrL2ttzJa1SZ3OusBPgWtoOZpzlWSLDLMNQg+W0yT1g0g+OYGNUVNi/MBUWQEcNyq76509vDXoNW8BCRPK0MJItmFosC+VfzVxZQ9cU0dVJR5W8vTOQdB04t89/1O/w1cDnyilFU=')
#handler = WebhookHandler('b0c8111bf70a2e8063d42c49ad1dd45d')
#BotBot
#line_bot_api = LineBotApi('JhzjS4H2a91ZATk82inkdJp6Tpy66EB18K7AFuQD1uVzJw2/4tJnu28MS62AlJXrzKpCe/5JbgHHR5Ly4kB4dKBuMCOJTK+7/qtiZSchmTdtRhdwFxnqEUNn+sB0KG/FEhVFZqYodSIZO5zPHK+1BwdB04t89/1O/w1cDnyilFU=')
#handler = WebhookHandler('b38646c2f6dd84fb3e2ffcf29e0f7e4b')
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

if channel_secret is None:
   print('Specify LINE_CHANNEL_SECRET as environment variable.')
   sys.exit(1)
if channel_access_token is None:
   print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
   sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

# function for create tmp dir for download content
def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise


@app.route("/", methods=['GET'])
def default_action():
    l = ptt.get_prices()
    s = ""
    for p in l:
        s += "%s %f บาท\n"%(p[0],p[1])
    return s

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        print("body" + body)

        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'




@handler.add(JoinEvent)
def handle_join(event):
   # group_id = event.source.group_id
   # line_bot_api.get_group_member_profile(group_id,member_id)
   # member_ids_res = line_bot_api.get_group_member_ids(group_id)
   # print(member_ids_res.member_ids)
   # print(member_ids_res.next)

    try:
       profile = line_bot_api.get_group_member_profile(
           event.source.group_id,
           'U8c9144cce38f797b77698267bf4307b1'
       )
       line_bot_api.reply_message(
           event.reply_token,
           [
               TextSendMessage(text='สวัสดีค่า'),
               StickerSendMessage(
                   package_id=1,
                   sticker_id=2
               )
           ]
       )  

    except LineBotApiError as e:
       print(e.status_code)
       print(e.error.message)
       print(e.error.details)
       line_bot_api.reply_message(
           event.reply_token,
           [
               TextSendMessage(text='หัวหน้าไม่อยู่ในห้องนี้\nไปละค่ะ\nบัย'),
               StickerSendMessage(
                   sticker_id=2
               )
           ]
       )
       line_bot_api.leave_group(event.source.group_id) 


@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
   # Handle webhook verification
    print("Sticker Message")
    if event.reply_token == "ffffffffffffffffffffffffffffffff":
       return

    line_bot_api.reply_message(
       event.reply_token,
       StickerSendMessage(
           package_id=event.message.package_id,
           sticker_id=event.message.sticker_id
       )
    )

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global latest_image_path


   # Handle webhook verification
    if event.reply_token == '00000000000000000000000000000000':
       return 'OK'
       
    if event.message.text == 'ออกไปได้แล้ว':
       if isinstance(event.source,SourceGroup):
           if event.source.user_id == 'U8c9144cce38f797b77698267bf4307b1':
               line_bot_api.reply_message(
                   event.reply_token,
                   [
                        TextSendMessage(text="บายบ๊ายจ้า"),
                        StickerSendMessage(
                            package_id=1,
                            sticker_id=1
                        )
                       
                    ]
               )
               line_bot_api.leave_group(event.source.group_id)
           else:
               line_bot_api.reply_message(
                   event.reply_token,
                   [
                        TextSendMessage(text="ไม่! ไม่ออกเว้ย"),
                        StickerSendMessage(
                            package_id=1,
                            sticker_id=6
                        )
                       
                    ]
                   
               )

    if event.message.text == 'ราคาน้ำมัน':
        l = ptt.get_prices()
        s = ""
        for p in l:
            s += "%s %.2f บาท\n"%(p[0],p[1])

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=s))
    elif event.message.text == 'วิเคราะห์รูป':
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text='สักครู่ค่ะ')
            ])

        # Process image
        try:
            lp = LicencePlate()
            result = lp.process(latest_image_path)
            s = lp.translate(result)

            line_bot_api.push_message(
                event.source.user_id, [
                    TextSendMessage(text=s)
                ])
        except Exception as e:
            print ('Exception:',type(e),e)
            line_bot_api.push_message(
                event.source.user_id, [
                    TextSendMessage(text='ไม่สามารถวิเคราะห์รูปได้')
                ])

    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text+'จ้า'))

@handler.add(MessageEvent, message=(ImageMessage, VideoMessage, AudioMessage))
def handle_content_message(event):
    global latest_image_path

    if isinstance(event.message, ImageMessage):
        ext = 'jpg'
    elif isinstance(event.message, VideoMessage):
        ext = 'mp4'
    elif isinstance(event.message, AudioMessage):
        ext = 'm4a'
    else:
        return

    message_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    dist_path = tempfile_path + '.' + ext
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)

    # Save image path
    latest_image_path = dist_path
    line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text='เก็บรูปให้แล้วค่ะ')
        ])



if __name__ == "__main__":
    app.run()