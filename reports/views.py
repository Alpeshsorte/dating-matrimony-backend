from rest_framework import generics, permissions

from .models import Report
from .serializers import ReportSerializer


class MyReportListCreateView(generics.ListCreateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Report.objects.filter(reporter=self.request.user).select_related('reported_user')
