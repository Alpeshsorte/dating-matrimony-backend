from django.urls import path

from .views import MyReportListCreateView

app_name = 'reports'

urlpatterns = [
    path('', MyReportListCreateView.as_view(), name='my-reports'),
]
