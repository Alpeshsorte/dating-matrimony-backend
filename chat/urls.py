from django.urls import path

from .views import ConversationListView, ConversationMessageView, StartConversationView

app_name = 'chat'

urlpatterns = [
    path('', ConversationListView.as_view(), name='conversation-list'),
    path('start/', StartConversationView.as_view(), name='conversation-start'),
    path('<int:conversation_id>/messages/', ConversationMessageView.as_view(), name='conversation-messages'),
]
