# domains/healthcare/views.py

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Patient, Prescription, InsuranceClaim, ClinicalRecord
from .serializers import PatientSerializer, PrescriptionSerializer, InsuranceClaimSerializer, ClinicalRecordSerializer


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['gender', 'blood_group']
    search_fields = ['full_name', 'mrn', 'email']


class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'patient']
    search_fields = ['medication', 'patient__full_name']
    ordering_fields = ['prescribed_date', 'created_at']


class InsuranceClaimViewSet(viewsets.ModelViewSet):
    queryset = InsuranceClaim.objects.all()
    serializer_class = InsuranceClaimSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['claim_number', 'patient__full_name']
    ordering_fields = ['claim_date', 'claim_amount', 'created_at']


class ClinicalRecordViewSet(viewsets.ModelViewSet):
    queryset = ClinicalRecord.objects.all()
    serializer_class = ClinicalRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient']
    search_fields = ['patient__full_name', 'diagnosis']
    ordering_fields = ['visit_date', 'created_at']
