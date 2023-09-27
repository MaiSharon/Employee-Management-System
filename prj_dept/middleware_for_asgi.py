from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.sessions.models import Session


class CustomAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # 從scope中獲取session_key
        session_key = scope.get("cookies", {}).get("sessionid", None)

        if session_key:
            # 從數據庫中讀取session
            session_data = await self.get_session_data(session_key)

            if session_data:
                # 解碼session數據並添加到scope中
                scope['session'] = session_data

        # 繼續執行下一個中間件或者consumer
        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_session_data(self, session_key):
        try:
            session = Session.objects.get(session_key=session_key)
            return session.get_decoded()
        except Session.DoesNotExist:
            return None
