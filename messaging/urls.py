from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('send/<int:listing_id>/', views.send_inquiry_view, name='send'),
    path('inbox/', views.inbox_view, name='inbox'),
    path('send-to-owner/<int:listing_id>/', views.send_inquiry_view, name='send'),
    path('thread/<int:partner_id>/', views.direct_chat_thread_view, name='thread'),
    path('reply/<int:parent_id>/', views.reply_message_view, name='reply'),
]