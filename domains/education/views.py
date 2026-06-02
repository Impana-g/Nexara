# domains/education/views.py

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Applicant, Program, Grant, AdmissionRecord
from .serializers import ApplicantSerializer, ProgramSerializer, GrantSerializer, AdmissionRecordSerializer


class ApplicantViewSet(viewsets.ModelViewSet):
    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['full_name', 'email']
    ordering_fields = ['gpa', 'test_score', 'application_date', 'created_at']


class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.all()
    serializer_class = ProgramSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['program_level']
    search_fields = ['program_name']


class GrantViewSet(viewsets.ModelViewSet):
    queryset = Grant.objects.all()
    serializer_class = GrantSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['grant_type', 'is_disbursed']
    search_fields = ['applicant__full_name']
    ordering_fields = ['grant_amount', 'awarded_date', 'created_at']


class AdmissionRecordViewSet(viewsets.ModelViewSet):
    queryset = AdmissionRecord.objects.all()
    serializer_class = AdmissionRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'enrollment_confirmed']
    search_fields = ['applicant__full_name', 'program__program_name']
    ordering_fields = ['admission_date', 'created_at']
