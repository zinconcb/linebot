from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import ptt

app = Flask(__name__)

line_bot_api = LineBotApi('GnZxefH4pGG1ubbStIfsAzQ4YLvReiC3reZWrL2ttzJa1SZ3OusBPgWtoOZpzlWSLDLMNQg+W0yT1g0g+OYGNUVNi/MBUWQEcNyq76509vDXoNW8BCRPK0MJItmFosC+VfzVxZQ9cU0dVJR5W8vTOQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('b0c8111bf70a2e8063d42c49ad1dd45d')

@app.route("/",methods=['GET'])
def default_action():
  return "Hello"



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


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    if event.message.text =='ราคาน้ำมัน':
        l = ptt.get_prices()
        s = ""
        for p in l:
            s +="%s %.2f บาท\n"%(p[0],p[1])

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=s))
    else:
   
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text+'ค่ะ'))


if __name__ == "__main__":
    app.run()

