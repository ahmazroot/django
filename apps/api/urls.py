
from django.urls import path
from . import views, test_views

app_name = 'api'

urlpatterns = [
    path('chat/call/', views.chat_call, name='chat_call'),
    path('chat/history/', views.chat_history, name='chat_history'),
    path('customer/add/', views.add_customer_data, name='add_customer'),
    path('tenant/info/', views.tenant_info, name='tenant_info'),
    path('test/', test_views.test_chat_interface, name='test_interface'),
]
