from datetime import datetime

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from settings.local import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET

from dept_app import models

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


@csrf_exempt
def callback(request):
    """  Line Bot 接收和處理用戶事件的入口點。將請求轉換為事件對象，並將這些對象傳遞給相應的處理函數。 """
    if request.method == "POST":
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            return HttpResponseBadRequest("what")

    return HttpResponse()


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="hi"))
    # 獲得用戶id
    user_id = event.source.user_id
    print(f"Received message from {user_id}")


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if '生日' in event.message.text:
        now = datetime.now()
        birthday_users = models.UserInfo.objects.filter(birthday__month=now.month)

        messages = []
        for user in birthday_users:
            messages.append(f"用戶名: {user.name}\n生日: {user.birthday}")

        if messages:
            response_message = "\n".join(messages)
        else:
            response_message = "這個月沒有用戶生日"

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response_message)
        )


def send_greeting(user_id, message):
    """ 椽送訊息給特定用戶 """
    line_bot_api.push_message(user_id, TextSendMessage(text=str(message)))

