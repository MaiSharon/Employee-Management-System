import json
import asyncio
import logging

from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from dept_app.models import Admin

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    """
    負責管理聊天室的WebSocket連接。

    主要功能：
    - 用戶加入/離開聊天室
    - 接收和發送消息
    - 實時更新用戶在線狀態
    - 實時更新新註冊的用戶

    Attributes:
    user_id (str): 用戶ID。
    username (str): 用戶名。
    room_name (str): 聊天室名稱。
    room_group_name (str): 聊天室群組名稱。
    is_connected (bool): 用戶是否已連接。

    Methods:
        connect: 處理新的 WebSocket 連接。
        disconnect: 斷開 WebSocket 連接。
        receive: 處理來自客戶端的訊息。
        chat_message: 處理聊天室群組的訊息。
        start_heartbeat: 心跳機制
        user_status: 更新用戶狀態給前端
        mark_user_online: 標記用戶為在線
        mark_user_offline: 標記用戶為離線
    """

    async def connect(self):
        """
        處理 WebSocket 連接

        Steps：
        1. 從session中提取用戶信息
            1.1 若有未認證用戶 'Anonymous' 則中斷連接
        2. 將用戶加入聊天室群組（這裡只有一個公開群)
        3. 啟動心跳機制用於保持用戶在線
        4. 標記用戶為在線
        """
        # 從session中提取用戶信息，如果沒有則設為"匿名"並停止連線
        session_info = self.scope.get('session', {}).get('info')
        try:
            self.user_id = session_info['id']
            self.username = session_info['name']
        except KeyError as e:
            self.user_id = 'Anonymous'
            logger.warning(f'Key not found: {e}, not get session setting user_id to Anonymous')
            await self.close()
            return  # 確保後面程式碼不會被執行


        # 記錄: 連線的用戶
        logger.info(f'{self.user_id} has come')

        # 設定聊天室名稱(從URL中提取)和群組名稱
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        print(self.room_group_name)

        # 將用戶加入聊天室群組(使用channel_layer)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # 接受WebSocket連接
        await self.accept()

        # 記錄: WebSocket連接成功
        logger.info('websocket connect')

        # 連接成功，設置 is_connected 為 True
        self.is_connected = True

        # 啟動心跳機制以實時更新用戶在線狀態
        asyncio.create_task(self.start_heartbeat())

        # 將用戶標記為在線
        await self.mark_user_online(self.user_id)

        # 記錄: 加入聊天室的用戶
        logger.info(f'{self.user_id} has joined')

    async def disconnect(self, close_code):
        """
        處理 WebSocket 斷開連接

        Steps:
        0. 若有未認證用戶 'Anonymous' 則忽略以下程式碼執行
        1. 將用戶從聊天室群組中移除
        2. 取消心跳機制任務

        Args:
            close_code (int): 斷開連線原因的狀態代碼

        Returns:
            None.
        """
        if self.user_id != 'Anonymous':
            # 記錄: WebSocket斷開
            logger.info('websocket disconnected')

            # 連接已斷開，設置 is_connected 為 False
            self.is_connected = False

            # 將用戶離開聊天室群組(使用channel_layer)
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

            await self.mark_user_offline(self.user_id)

            # 記錄: 離開聊天室的用戶
            logger.info(f'{self.user_id} has left')

    async def receive(self, text_data):
        """
        接收與處理客戶端發來的消息。

        Steps:
        1. 解析收到的 JSON 格式的訊息。
        2. 如果訊息包含 'message' 這個鍵，則將其轉發到聊天室群組。

        Args:
            text_data (str): 客戶端發來的 JSON 格式的文本數據。

        Returns:
            None: 訊息將會被轉發到聊天室群組。

        Raises:
            json.JSONDecodeError: 當JSON格式不正確。
        """
        try:
            text_data_json = json.loads(text_data)
        except json.JSONDecodeError:
            logger.warning('Invalid JSON format received')
            return

        if 'message' in text_data_json:
            message = text_data_json['message']
        else:
            logger.warning('No "message" key in received data')
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.username
            }
        )
        logger.info(f'Forwarded message: {message}')

    # 從這裡發送新管理員的訊息到前端
    async def new_admin(self, event):
        # Extract the admin information from the event
        admin_info = event['user']

        # Prepare a message to send to the WebSocket client
        message = {
            'type': 'new_admin',
            'user': {
                'id': admin_info['id'],
                'username': admin_info['username'],
                'is_online': False  # You can change this depending on your logic
            },
            'message': 'A new admin account has been created.'
        }

        # Send the message to the WebSocket
        await self.send(text_data=json.dumps(message))

    async def chat_message(self, event):
        """
        處理從聊天室群組接收到的消息。

        Steps:
        1. 從事件中提取消息內容和發送者的用戶名。
        2. 將消息以 JSON 格式發送到 WebSocket 。

        Args:
            event (dict): 包含 message (發送的文本內容)和 username (發送者的用戶名)的信息。

        Returns:
            None: 消息將被發送到 WebSocket。

        Raises:
            KeyError: 當 event 的 'message' 或 'username' 不存在。
        """
        try:
            message = event['message']
            username = event['username']
        except KeyError:
            logger.warning('Missing key in event')
            return

        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'username': username
        }))
        logger.info(f"Sent message '{message}' from {username} to WebSocket")

    async def start_heartbeat(self):
        """
        進行心跳機制以維護用戶的在線狀態。如果心跳機制中斷，將觸發其他方法以標記用戶為離線。

        Steps:
        1. 每隔段時間（30秒）發送一個心跳包到前端。
        2. 確認 WebSocket 連接沒斷開（self.is_connected 為 True）。

        Args:
            無

        Returns:
            None: 此函數不返回任何值。

        Raises:
            KeyError: 當 'user_id' 不存在。
            json.JSONDecodeError: 當JSON格式不正確。
            Exception: 其他未指定的錯誤。
        """
        while True:
            await asyncio.sleep(30)  # Sleep for 30 seconds

            if not self.is_connected:
                logger.info('Connection terminated, stopping heartbeat')
                break

            try:
                if not self.is_connected:
                    logger.info('Connection terminated, stopping heartbeat')
                    break
                await self.send(text_data=json.dumps({'type': 'heartbeat'}))
                logger.info('Heartbeat packet sent')
            except json.JSONDecodeError:
                logger.error('Incorrect JSON format')
                break
            except Exception as e:
                logger.error(f'Unknown error of type: {type(e)}')

            try:
                if not self.is_connected:
                    logger.info('Connection terminated, stopping heartbeat')
                    break
                await self.mark_user_online(self.user_id)
                logger.info(f'User {self.user_id} marked online')
            except KeyError:
                logger.error('user_id not found, terminating heartbeat process')
                break
            except Exception as e:
                logger.error(f'Unknown error of type: {type(e)}')

    async def user_status(self, event):
        """
        更新用戶的在線狀態並發送到前端。

        Args:
            event (dict): 包含用戶 ID 和在線狀態的事件字典。
                - user_id (str): 用戶的唯一識別符。
                - is_online (bool): 用戶的在線狀態。

        Returns:
            None: 此方法不返回任何值。

        Raises:
            KeyError: 如果 'user_id' 或 'is_online' 不存在於 event 字典。
            JSONDecodeError: 如果 JSON 格式不正確。
        """
        try:
            user_id = event['user_id']
            is_online = event['is_online']
        except KeyError:
            logger.warning(f'user_id or is_online not found')
            return

        try:
            await self.send(text_data=json.dumps({
                'type': 'user_status',
                'user_id': user_id,
                'is_online': is_online
            }))
            logger.info(f'Successfully sent user_status for user_id={user_id}, is_online={is_online}')
        except json.JSONDecodeError:
            logger.warning('Incorrect JSON format')

    @database_sync_to_async
    def mark_user_online(self, user_id):
        """
        將指定的用戶標記為上線狀態並向前端發送更新。

        Steps：
        1. 根據提供的 user_id 查找對應的 Admin 對象。
        2. 將 Admin 對象的 is_online 屬性設置為 True。
        3. 通過 WebSocket 向前端發送更新後的在線狀態。

        Args:
            user_id (str): 要標記為上線的用戶的 ID。

        Returns:
            None: 此方法不返回任何值。

        Raises:
            Admin.DoesNotExist: 如果 user_id 在 Admin 對象中不存在。
        """
        try:
            user = Admin.objects.get(id=user_id)
            user.is_online = True
            user.save()

            # Log the status change
            logger.info(f"User {user_id} marked as online")

            # Send user_status message
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'user_status',
                    'user_id': user_id,
                    'is_online': True,
                }
            )
        except Admin.DoesNotExist:
            logger.warning('User ID does not exist in Admin model')

    @database_sync_to_async
    def mark_user_offline(self, user_id):
        """
        將指定的用戶標記為離線狀態並向前端發送更新。

        步驟：
        1. 根據提供的 user_id 查找對應的 Admin 對象。
        2. 將 Admin 對象的 is_online 屬性設置為 False。
        3. 通過 WebSocket 向前端發送更新後的在線狀態。

        Args:
            user_id (str): 要標記為離線的用戶的 ID。

        Returns:
            None: 此方法不返回任何值。

        Raises:
            Admin.DoesNotExist: 如果指定的 user_id 在 Admin 對象中不存在。
        """
        try:
            user = Admin.objects.get(id=user_id)
            user.is_online = False
            user.save()

            # Log the status change
            logger.info(f"User {user_id} marked as online")

            # Send user_status message
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'user_status',
                    'user_id': user_id,
                    'is_online': False,
                }
            )
        except Admin.DoesNotExist:
            logger.warning('User ID does not exist in Admin model')





