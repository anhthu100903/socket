from channels.generic.websocket import AsyncWebsocketConsumer
import json

connected_clients = {}

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        client_id = self.scope["client"][1]
        connected_clients[client_id] = {'consumer': self, 'last_message': None}
        await self.accept()
        await self.send(text_data=json.dumps({'message': f"Chào mừng Client {client_id}!"}))
        print(f"✅ Client {client_id} đã kết nối.")

    async def disconnect(self, close_code):
        client_id = self.scope["client"][1]
        if client_id in connected_clients:
            del connected_clients[client_id]
        print(f"❌ Client {client_id} đã ngắt kết nối.")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get('message', '')
            client_id = self.scope["client"][1]

            connected_clients[client_id]['last_message'] = message
            print(f"📨 Client {client_id} gửi: {message}")

            # Gửi lại tin nhắn cho client
            await self.send(text_data=json.dumps({'message': f"📬 Server nhận: {message}"}))

            # Gửi tin nhắn mới nhất đến admin
            await self.send_admin_update(client_id, message)

            if message.lower() == "quit":
                await self.send(text_data=json.dumps({'message': "Server: Tạm biệt!"}))
                await self.close()

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({'message': "❌ Dữ liệu không hợp lệ!"}))

    async def send_admin_update(self, client_id, message):
        # Gửi tin nhắn mới nhất đến admin
        for admin in connected_clients.values():
            if isinstance(admin['consumer'], AdminConsumer):
                await admin['consumer'].send(text_data=json.dumps({
                    'type': 'newMessage',
                    'clientId': client_id,
                    'message': message
                }))

class AdminConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("Admin đã kết nối.")
        await self.send_connected_clients()

    async def disconnect(self, close_code):
        print("Admin đã ngắt kết nối.")

    async def receive(self, text_data):
        data = json.loads(text_data)
        client_id = int(data.get('target_client'))
        message = data.get('message')
        if client_id in connected_clients:
            await connected_clients[client_id]['consumer'].send(text_data=json.dumps({'message': f"💬 Tin nhắn từ Admin: {message}"}))
            await self.send(text_data=json.dumps({'type': 'status', 'message': f"✅ Gửi thành công đến Client {client_id}"}))
        else:
            await self.send(text_data=json.dumps({'type': 'status', 'message': f"❌ Không tìm thấy Client {client_id}"}))

    async def send_connected_clients(self):
        client_data = [{'id': client_id, 'lastMessage': details['last_message']} for client_id, details in connected_clients.items()]
        await self.send(text_data=json.dumps({'type': 'clients', 'clients': client_data}))
