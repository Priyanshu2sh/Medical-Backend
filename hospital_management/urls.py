from django.urls import path
from .views import HospitalCreateAPIView, HMSUserRegisterAPIView, HMSUserLoginAPIView, PatientDetailsCreateAPIView, PatientDetailsUpdateAPIView, FindingsCreateAPIView, FindingsByPatientAPIView, FindingsUpdateAPIView, AllergiesCreateAPIView, AllergiesByPatientAPIView, AdminAddUserAPIView, GetAllUsersAPIView, PatientFamilyHistoryCreateView, PatientFamilyHistoryByPatientView, HMSUserUpdateView, HMSUserDeleteView, HMSUserStatusUpdateView, CreatePastHospitalHistoryAPIView, GetPastHospitalHistoryByPatientAPIView, MedicalHistoryCurrentHospitalCreateAPIView, MedicalHistoryCurrentHospitalByPatientAPIView, DiseasesCreateAPIView, DiseasesByPatientAPIView, UpdateDiseaseStatusAPIView, OngoingMedicationCreateAPIView, OngoingMedicationByPatientAPIView, MedicineCreateAPIView, ClinicalNotesCreateAPIView, ClinicalNotesByPatientAPIView, CertificateCreateAPIView, PatientFullHistoryAPIView, AttachmentsCreateAPIView, OPDCreateAPIView, OPDStatusUpdateAPIView, OPDListByDoctorAPIView, PrescriptionCreateAPIView, AllMedicineNamesAPIView, GetPrescriptionsByPatientAPIView, BillperticularsCreateAPIView, BillCreateAPIView, GetBillsByPatientAPIView, UpdateBillPaymentAPIView, BillPerticularsDeleteAPIView, BillPerticularsUpdateAPIView, InvoiceListAPIView, WardCreateAPIView, BedCreateAPIView,IPDCreateAPIView, GetBedsByWardAPIView, UpdateBedStatusAPIView, GetAllWardsAPIView, IPDTransferDoctorAPIView, IPDByDoctorAPIView, WardWithBedsAPIView

urlpatterns = [

    path('hospital-and-admin/', HospitalCreateAPIView.as_view(), name='create-hospital'),
    path('hmsuser/register/', HMSUserRegisterAPIView.as_view(), name='hmsuser-register'),
    path('hmsuser/login/', HMSUserLoginAPIView.as_view(), name='hmsuser-login'),
    path('hmsuser/admin/add-user/', AdminAddUserAPIView.as_view(), name='admin-add-user'),
    path('hmsuser/get-users-all/', GetAllUsersAPIView.as_view(), name='get-all-users'),
    path('hmsuser/update/<int:user_id>/', HMSUserUpdateView.as_view(), name='update-hms-user'),
    path('hmsuser/delete/<int:user_id>/', HMSUserDeleteView.as_view(), name='delete-hms-user'),
    path('hmsuser/status/<int:user_id>/', HMSUserStatusUpdateView.as_view(), name='hmsuser-status-toggle'),

    path('patient-details/', PatientDetailsCreateAPIView.as_view(), name='patient-create'),
    path('patient-detail/', PatientDetailsCreateAPIView.as_view(), name=' get-patient-create'),
    path('patient/update/<int:pk>/', PatientDetailsUpdateAPIView.as_view(), name='patient-update'),
    path('patient/delete/<int:pk>/', PatientDetailsUpdateAPIView.as_view(), name='patient-update'),

    # EX Finding API
    path('finding/', FindingsCreateAPIView.as_view(), name='exfinding-create'),
    path('finding/patient/<int:patient_id>/', FindingsByPatientAPIView.as_view(), name='exfinding-by-patient'),
    path('findings/update/<int:pk>/', FindingsUpdateAPIView.as_view(), name='findings-update'),

    path('allergies/', AllergiesCreateAPIView.as_view(), name='allergies-create'),
    path('patients/<int:patient_id>/allergies/', AllergiesByPatientAPIView.as_view(), name='patient-allergies'),

    path('family-history/', PatientFamilyHistoryCreateView.as_view(), name='create-family-history'),
    path('family-history/patient/<int:patient_id>/', PatientFamilyHistoryByPatientView.as_view(), name='get-family-history-by-patient'),

    path('past-history/', CreatePastHospitalHistoryAPIView.as_view(), name='create-past-history'),
    path('past-history/<int:patient_id>/', GetPastHospitalHistoryByPatientAPIView.as_view(), name='get-past-history-by-patient'),

    path('past-history/current-hospital/', MedicalHistoryCurrentHospitalCreateAPIView.as_view(), name='create-current-hospital-history'),
    path('past-history/current-hospital/patient/<int:patient_id>/', MedicalHistoryCurrentHospitalByPatientAPIView.as_view(), name='get-current-hospital-history'),

    path('diseases/', DiseasesCreateAPIView.as_view(), name='create-disease'),
    path('diseases/patient/<int:patient_id>/', DiseasesByPatientAPIView.as_view(), name='get-diseases-by-patient'),
    path('diseases/<int:pk>/update-status/', UpdateDiseaseStatusAPIView.as_view(), name='update-disease-status'),

    path('ongoing-medication/', OngoingMedicationCreateAPIView.as_view(), name='ongoing-medication-create'),
    path('ongoing-medication/patient/<int:patient_id>/', OngoingMedicationByPatientAPIView.as_view(), name='ongoing-medication-by-patient'),
 
    path('clinical-notes/', ClinicalNotesCreateAPIView.as_view(), name='create-clinical-note'),
    path('clinical-notes/patient/<int:patient_id>/', ClinicalNotesByPatientAPIView.as_view(), name='get-clinical-notes-by-patient'),

    path('medicine/', MedicineCreateAPIView.as_view(), name='create-medicine'),
    path('medicines/patient/<int:patient_id>/', MedicineCreateAPIView.as_view(), name='get-medicines-by-patient'),

    path('certificates/', CertificateCreateAPIView.as_view(), name='create-certificate'),
    path('certificate/patient/<int:patient_id>/', CertificateCreateAPIView.as_view(), name='certificate-by-patient'),

    path('patient/full-history/<int:patient_id>/', PatientFullHistoryAPIView.as_view(), name='patient-full-history'),       #for get al patient history 

    path('attachments/', AttachmentsCreateAPIView.as_view(), name='add-attachment'),
    path('attachments/patient/<int:patient_id>/', AttachmentsCreateAPIView.as_view(), name='get-attachments-by-patient'),

    path('opd/', OPDCreateAPIView.as_view(), name='create-opd'),
    path('opds/', OPDCreateAPIView.as_view(), name='get-all-opd'),
    path('opd/<int:opd_id>/update-status/', OPDStatusUpdateAPIView.as_view(), name='update-opd-status'),
    path('opd/doctor/<int:doctor_id>/', OPDListByDoctorAPIView.as_view(), name='opd-by-doctor'),

    path('prescription/', PrescriptionCreateAPIView.as_view(), name='create-prescription'),
    path('prescriptions/', PrescriptionCreateAPIView.as_view(), name='get-all-prescriptions'),
    path('prescription/medicine-names/', AllMedicineNamesAPIView.as_view(), name='all-medicine-names'),
    path('prescription/patient/<int:patient_id>/', GetPrescriptionsByPatientAPIView.as_view(), name='get-prescriptions-by-patient'),

    path('bill-perticulars/', BillperticularsCreateAPIView.as_view(), name='bill-perticulars-create'),
    path('bill/particulars/', BillperticularsCreateAPIView.as_view(), name='bill-particulars-list'),
    path('bill-particulars/delete/<int:pk>/', BillPerticularsDeleteAPIView.as_view(), name='delete-bill-particular'),
    path('bill-perticulars/update/<int:pk>/', BillPerticularsUpdateAPIView.as_view(), name='update-bill-perticular'),
    path('bill/', BillCreateAPIView.as_view(), name='bill-create'),
    path('bills/all/', BillCreateAPIView.as_view(), name='get-all-bills'),
    path('bill/patient/<int:patient_id>/', GetBillsByPatientAPIView.as_view(), name='get-bills-by-patient'),
    path('bill/<int:pk>/update-payment/', UpdateBillPaymentAPIView.as_view(), name='update-bill-payment'),
    path('invoices/', InvoiceListAPIView.as_view(), name='invoice-list'),
    
    # IPD
    path('wards/', WardCreateAPIView.as_view(), name='create-ward'),
    path('wards_all/', GetAllWardsAPIView.as_view(), name='get-all-wards'),


    path('bed/', BedCreateAPIView.as_view(), name='create-bed'),
    path('beds/ward/<int:ward_id>/', GetBedsByWardAPIView.as_view(), name='get-beds-by-ward'),
    path('beds/<int:bed_id>/update-status/', UpdateBedStatusAPIView.as_view(), name="update-bed-status"),
    path('wards-beds/', WardWithBedsAPIView.as_view(), name='wards-beds'),


    path("ipd/", IPDCreateAPIView.as_view(), name="ipd-create"),
    path('ipd-list/', IPDCreateAPIView.as_view(), name='ipd-list'),
    path('ipd/by-doctor/<int:doctor_id>/', IPDByDoctorAPIView.as_view(), name='ipd-by-doctor'),
    path('ipd/<int:pk>/transfer-doctor/', IPDTransferDoctorAPIView.as_view(), name='ipd-update-doctor'),

]
