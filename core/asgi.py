import os
import sys

# --- FORCE VENV PATH INJECTION ---
venv_site_packages = r'C:\Users\LENOVO\divine-digital-forum\venv\Lib\site-packages'
if venv_site_packages not in sys.path:
    sys.path.append(venv_site_packages)
# ---------------------------------

import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import dashboard.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(dashboard.routing.websocket_urlpatterns)
    ),
})