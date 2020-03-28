# mysite/routing.py
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import chat.routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})


# This root routing configuration specifies that when a connection is made to the Channels development server, 
# the ProtocolTypeRouter will first inspect the type of connection. If it is a WebSocket connection (ws:// or wss://),
#  the connection will be given to the AuthMiddlewareStack.
# The AuthMiddlewareStack will populate the connection’s scope with a reference to the currently authenticated user, 
# similar to how Django’s AuthenticationMiddleware populates the request object of a view function with the currently
#  authenticated user. (Scopes will be discussed later in this tutorial.) Then the connection will be given to the URLRouter.
# The URLRouter will examine the HTTP path of the connection to route it to a particular consumer, based on the provided url patterns.