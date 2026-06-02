# domains/hr/views.py

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Employee, JobRequisition, OfferLetter, PayrollRecord
from .serializers import EmployeeSerializer, JobRequisitionSerializer, OfferLetterSerializer, PayrollRecordSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'employment_type', 'department']
    search_fields = ['full_name', 'email', 'designation']
    ordering_fields = ['full_name', 'date_of_joining', 'salary']


class JobRequisitionViewSet(viewsets.ModelViewSet):
    queryset = JobRequisition.objects.all()
    serializer_class = JobRequisitionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'department']
    search_fields = ['title', 'requested_by']
    ordering_fields = ['created_at', 'budget_max']


class OfferLetterViewSet(viewsets.ModelViewSet):
    queryset = OfferLetter.objects.all()
    serializer_class = OfferLetterSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'department']
    search_fields = ['candidate_name', 'designation']
    ordering_fields = ['created_at', 'offered_salary']


class PayrollRecordViewSet(viewsets.ModelViewSet):
    queryset = PayrollRecord.objects.all()
    serializer_class = PayrollRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_exception', 'month']
    search_fields = ['employee__full_name', 'month']
    ordering_fields = ['month', 'net_salary']
