from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('clients/', include('clients.urls', namespace='clients')),
    path('messages/', include('messages_app.urls', namespace='messages_app')),
    path('mailings/', include('mailings.urls', namespace='mailings')),
]
