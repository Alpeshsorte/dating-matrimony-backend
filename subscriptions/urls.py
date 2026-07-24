from django.urls import path

from .views import ActivePlanListView, MySubscriptionListView

app_name = 'subscriptions'

urlpatterns = [
    path('plans/', ActivePlanListView.as_view(), name='plans'),
    path('me/', MySubscriptionListView.as_view(), name='my-subscriptions'),
]
