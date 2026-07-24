from django.urls import path

from .views import MatchActionView, MatchCreateView, MyMatchListView

app_name = 'dating'

urlpatterns = [
    path('', MyMatchListView.as_view(), name='my-matches'),
    path('request/', MatchCreateView.as_view(), name='match-request'),
    path('<int:match_id>/action/', MatchActionView.as_view(), name='match-action'),
]
