from django.urls import path

from . import views

app_name = "chatbot"

urlpatterns = [
    path("chatbot/", views.chat_page, name="chat"),
    path("chatbot/api/history/", views.chat_history, name="api_history"),
    path("chatbot/api/message/", views.chat_api, name="api_message"),
]
