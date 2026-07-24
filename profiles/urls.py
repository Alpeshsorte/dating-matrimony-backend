from django.urls import path

from .views import MyProfileView, PublicProfileListView

app_name = 'profiles'

urlpatterns = [
    path('', PublicProfileListView.as_view(), name='public-list'),
    path('me/', MyProfileView.as_view(), name='me'),
]
