import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        # Join room group
        # adding this instance/channel to the group 
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        # type is chat_message so there must be a function named chat_message or it will give
        # error - No handler for message type chat_message
        # below lines will call chat_message and send message to all instances connected to this group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))

# ================================================== #

# BEHAVIOUR-
# When a user posts a message, a JavaScript function will transmit the message over WebSocket to a 
# ChatConsumer. The ChatConsumer will receive that message and forward it to the group corresponding 
# to the room name. Every ChatConsumer in the same group (and thus in the same room) will then receive 
# the message from the group and forward it over WebSocket back to JavaScript, where it will be appended
# to the chat log.

# ================================================== #

# WHAT IS CHANNEL LAYER-
# A channel layer is a kind of communication system. It allows multiple consumer instances to talk with each other,
#  and with other parts of Django.
# A channel layer provides the following abstractions:

# A channel is a mailbox where messages can be sent to. Each channel has a name. Anyone who has the name of a 
# channel can send a message to the channel.
# A group is a group of related channels. A group has a name. Anyone who has the name of a group can 
# add/remove a channel to the group by name and send a message to all channels in the group. It is not
#  possible to enumerate what channels are in a particular group.
# Every consumer instance has an automatically generated unique channel name, and so can be communicated
#  with via a channel layer.

# In our chat application we want to have multiple instances of ChatConsumer in the same room
#  communicate with each other. To do that we will have each ChatConsumer add its channel to a group 
#  whose name is based on the room name. That will allow ChatConsumers to transmit messages to all other ChatConsumers in the same room


# ================================================== #

# EXPLANATION: 
# Several parts of the new ChatConsumer code deserve further explanation:


# self.scope['url_route']['kwargs']['room_name']
# Obtains the 'room_name' parameter from the URL route in chat/routing.py that opened the WebSocket connection to the consumer.
# Every consumer has a scope that contains information about its connection, including in particular any positional or keyword arguments from the URL route and the currently authenticated user if any.


# self.room_group_name = 'chat_%s' % self.room_name
# Constructs a Channels group name directly from the user-specified room name, without any quoting or escaping.
# Group names may only contain letters, digits, hyphens, and periods. Therefore this example code will fail on room names that have other characters.


# async_to_sync(self.channel_layer.group_add)(...)
# Joins a group.
# The async_to_sync(…) wrapper is required because ChatConsumer is a synchronous WebsocketConsumer but it is calling an asynchronous channel layer method. (All channel layer methods are asynchronous.)
# Group names are restricted to ASCII alphanumerics, hyphens, and periods only. Since this code constructs a group name directly from the room name, it will fail if the room name contains any characters that aren’t valid in a group name.


# self.accept()
# Accepts the WebSocket connection.
# If you do not call accept() within the connect() method then the connection will be rejected and closed. You might want to reject a connection for example because the requesting user is not authorized to perform the requested action.
# It is recommended that accept() be called as the last action in connect() if you choose to accept the connection.


# async_to_sync(self.channel_layer.group_discard)(...)
# Leaves a group.


# async_to_sync(self.channel_layer.group_send)
# Sends an event to a group.
# An event has a special 'type' key corresponding to the name of the method that should be invoked on consumers that receive the event.

# ================================================== #
# https://channels.readthedocs.io/en/latest/tutorial/part_3.html
# SYNCRONOUS OR ASYNCRONOUS
# The ChatConsumer that we have written is currently synchronous. Synchronous consumers are convenient because they can call
#  regular synchronous I/O functions such as those that access Django models without writing special code. However asynchronous
#   consumers can provide a higher level of performance since they don’t need to create additional threads when handling requests.

# ChatConsumer only uses async-native libraries (Channels and the channel layer) and in particular it does not 
# access synchronous Django models. Therefore it can be rewritten to be asynchronous without complications.