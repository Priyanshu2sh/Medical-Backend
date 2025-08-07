from django.urls import path
from .views import HospitalCreateAPIView, HMSUserRegisterAPIView, HMSUserLoginAPIView, PatientDetailsCreateAPIView, PatientDetailsUpdateAPIView, FindingsCreateAPIView, FindingsByPatientAPIView, FindingsUpdateAPIView, AllergiesCreateAPIView, AllergiesByPatientAPIView, AdminAddUserAPIView, GetAllUsersAPIView, PatientFamilyHistoryCreateView, PatientFamilyHistoryByPatientView, HMSUserUpdateView, HMSUserDeleteView, HMSUserStatusUpdateView, CreatePastHospitalHistoryAPIView, GetPastHospitalHistoryByPatientAPIView, MedicalHistoryCurrentHospitalCreateAPIView, MedicalHistoryCurrentHospitalByPatientAPIView, DiseasesCreateAPIView, DiseasesByPatientAPIView, UpdateDiseaseStatusAPIView, OngoingMedicationCreateAPIView, OngoingMedicationByPatientAPIView, MedicineCreateAPIView, ClinicalNotesCreateAPIView, ClinicalNotesByPatientAPIView, CertificateCreateAPIView, PatientFullHistoryAPIView, AttachmentsCreateAPIView, OPDCreateAPIView, OPDStatusUpdateAPIView, OPDListByDoctorAPIView, PrescriptionCreateAPIView, AllMedicineNamesAPIView, GetPrescriptionsByPatientAPIView, BillperticularsCreateAPIView, BillCreateAPIView, GetBillsByPatientAPIView, UpdateBillPaymentAPIView, BillPerticularsDeleteAPIView, BillPerticularsUpdateAPIView, InvoiceListAPIView, WardCreateAPIView, BedCreateAPIView,IPDCreateAPIView, GetBedsByWardAPIView, UpdateBedStatusAPIView, GetAllWardsAPIView, IPDTransferDoctorAPIView, IPDByDoctorAPIView, WardWithBedsAPIView, SupplierCreateAPIView, PrescriptionPaymentUpdateAPIView, PharmacyBillCreateAPIView, UpdatePharmacyBillPaymentView, PharmacyMedicineCreateView, MedicineStockCreateView, StockTransactionListView, PrescriptionWithBillAPIView, UpdateDoctorAvailabilityView, PatientRegisterView, VerifyPatientOTPView, PatientLoginView, AvailableDoctorsView, PatientForgotPasswordAPIView, PatientResetPasswordAPIView, PatientVerifyOTPAPIView, GetHMSUserWithHospitalView, DoctorPastOPDView, GetHospitalByIdView, CreatePatientAppointmentAPIView, AppointmentStatusUpdateView, PatientAppointmentResponseAPIView, DoctorAppointmentsAPIView, PatientAppointmentsAPIView, DoctorTimetableCreateAPIView, DoctorTimetableByDoctorAPIView, UpdateDoctorTimetableAPIView, LabReportCreateAPIView, LabReportsByLabAssistantAPIView, LabReportDeleteAPIView, GetPatientDetailsByIdView, BirthRecordCreateView, DeathReportCreateView, PatientCancelAppointmentAPIView, DoctorProfileUpdateAPIView, DoctorProfileCreateAPIView, AllPastOPDView, DoctorProfileDetailAPIView, HospitalDashboardStatsAPIView, TodayOPDListView, PharmacyOutBillCreateAPIView, PharmacyOutBillUpdateAPIView, PharmacyInvoiceListView, GetAllPharmacyOutInvoicesView

urlpatterns = [

    path('hospital-and-admin/', HospitalCreateAPIView.as_view(), name='create-hospital'),
    # path('hospital/get-by-id/', GetHospitalByIdView.as_view(), name='get-hospital-by-id'),
    path('hospital/<str:hospital_id>/', GetHospitalByIdView.as_view(), name='get-hospital-by-id'),

    path('hmsuser/register/', HMSUserRegisterAPIView.as_view(), name='hmsuser-register'),
    path('hmsuser/login/', HMSUserLoginAPIView.as_view(), name='hmsuser-login'),
    path('hmsuser/admin/add-user/', AdminAddUserAPIView.as_view(), name='admin-add-user'),
    path('hmsuser/get-users-all/', GetAllUsersAPIView.as_view(), name='get-all-users'),
    path('hmsuser/doctors/available/', AvailableDoctorsView.as_view(), name='available_doctors'),      #list of available doctors
    path('hmsuser/update/<int:user_id>/', HMSUserUpdateView.as_view(), name='update-hms-user'),
    path('hmsuser/delete/<int:user_id>/', HMSUserDeleteView.as_view(), name='delete-hms-user'),
    path('hmsuser/status/<int:user_id>/', HMSUserStatusUpdateView.as_view(), name='hmsuser-status-toggle'),
    path('hmsuser/doctor/<int:doctor_id>/availability/', UpdateDoctorAvailabilityView.as_view(), name='update-doctor-availability'),
    path('hospital-hms-user/<int:user_id>/', GetHMSUserWithHospitalView.as_view(), name='get-hms-user-with-hospital'),  #for profile section
    path('hmsuser/doctor-profile/create/', DoctorProfileCreateAPIView.as_view(), name='doctor-profile-create'),
    path('hmsuser/doctor-profile/update/<doctor_id>/', DoctorProfileUpdateAPIView.as_view(), name='update-doctor-profile'),
    path('hmsuser/doctor-profile/<int:doctor_id>/', DoctorProfileDetailAPIView.as_view(), name='doctor-profile-detail'),

    path('patient-details/', PatientDetailsCreateAPIView.as_view(), name='patient-create'),
    path('patient-detail/', PatientDetailsCreateAPIView.as_view(), name=' get-patient-create'),
    path('patient/<int:patient_id>/', GetPatientDetailsByIdView.as_view(), name='get-patient-details'),
    path('patient/update/<int:pk>/', PatientDetailsUpdateAPIView.as_view(), name='patient-update'),
    path('patient/delete/<int:pk>/', PatientDetailsUpdateAPIView.as_view(), name='patient-update'),
    path('patient/register/', PatientRegisterView.as_view(), name='patient_register'),
    path('patient/verify-otp/', VerifyPatientOTPView.as_view(), name='verify_patient_otp'),
    path('patient/login/', PatientLoginView.as_view(), name='patient_login'),
    path('patient/forgot-password/', PatientForgotPasswordAPIView.as_view(), name='patient_forgot_password'),
    path('patient/forget-password/verify-otp/', PatientVerifyOTPAPIView.as_view(), name='patient-verify-otp'),
    path('patient/reset-password/', PatientResetPasswordAPIView.as_view(), name='patient_reset_password'),

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
    path('opd/past/doctor/<int:doctor_id>/', DoctorPastOPDView.as_view(), name='doctor-past-opd'),
    path('opd/past-all/', AllPastOPDView.as_view(), name='past-all-opd'),
    path('opd/today/', TodayOPDListView.as_view(), name="todays-opd-list"),


    path('prescription/', PrescriptionCreateAPIView.as_view(), name='create-prescription'),
    path('prescriptions/', PrescriptionCreateAPIView.as_view(), name='get-all-prescriptions'),
    path('prescription/medicine-names/', AllMedicineNamesAPIView.as_view(), name='all-medicine-names'),
    path('prescription/patient/<int:patient_id>/', GetPrescriptionsByPatientAPIView.as_view(), name='get-prescriptions-by-patient'),
    path('supplier/', SupplierCreateAPIView.as_view(), name='supplier-create'),
    path('suppliers/', SupplierCreateAPIView.as_view(), name='supplier-create'),
    path('prescription/<int:pk>/update/', PrescriptionPaymentUpdateAPIView.as_view(), name='update-prescription-payment'),

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

    path('pharmacy-bill/', PharmacyBillCreateAPIView.as_view(), name='pharmacy-bill-create'),
    path('pharmacy-bill/<int:pk>/update/', UpdatePharmacyBillPaymentView.as_view(), name='update-prescription-payment'),
    path('prescriptions/with-bills/', PrescriptionWithBillAPIView.as_view(), name='pharmacy-bill-by-prescription'),
    path("pharmacy-invoices/", PharmacyInvoiceListView.as_view(), name="pharmacy-invoice-list"),

    path('pharmacy/out-bill/', PharmacyOutBillCreateAPIView.as_view(), name="create-pharmacy-out-bill"),
    path('pharmacy/out-bills/', PharmacyOutBillCreateAPIView.as_view(), name="get-pharmacy-out-bill"),
    path('pharmacy/out-bill/<int:bill_id>/update/', PharmacyOutBillUpdateAPIView.as_view(), name="update-pharmacy-out-bill"),
    path('pharmacy-out/invoices/', GetAllPharmacyOutInvoicesView.as_view(), name='get_all_pharmacy_out_invoices'),


    path('pharmacy/medicine/', PharmacyMedicineCreateView.as_view(), name='pharmacy-medicine-create'),
    path('pharmacy-medicine/', PharmacyMedicineCreateView.as_view(), name='pharmacy-medicine-get'),
    path('pharmacy/medicine-stock/', MedicineStockCreateView.as_view(), name='medicine-stock-create'),
    path('pharmacy/medicine-stocks/', MedicineStockCreateView.as_view(), name='medicine-stock-create'),
    path('pharmacy/transactions/', StockTransactionListView.as_view(), name='pharmacy-stock-transactions'),

    path('doctor-timetable/', DoctorTimetableCreateAPIView.as_view(), name='create-doctor-timetable'),
    path('doctor-timetable/<int:doctor_id>/', DoctorTimetableByDoctorAPIView.as_view(), name='get-doctor-timetable'),
    path('doctor-timetable/<int:pk>/update/', UpdateDoctorTimetableAPIView.as_view()),

    path('patient/appointment/', CreatePatientAppointmentAPIView.as_view(), name='create-patient-appointment'),
    path('doctor/<int:doctor_id>/appointments/', DoctorAppointmentsAPIView.as_view()),
    path('patient/<int:patient_id>/appointments/', PatientAppointmentsAPIView.as_view()),
    path('patient/appointment/<int:appointment_id>/doctor-status/', AppointmentStatusUpdateView.as_view()),
    path('patient/appointment/<int:pk>/patient-response/', PatientAppointmentResponseAPIView.as_view(), name='patient-response'),
    path('patient/appointment/<int:appointment_id>/cancel/', PatientCancelAppointmentAPIView.as_view(), name='patient-cancel-appointment'),

    path('lab-report/', LabReportCreateAPIView.as_view(), name='create-lab-report'),
    path('lab-reports/by-lab-assistant/<int:lab_assistant_id>/', LabReportsByLabAssistantAPIView.as_view(), name='lab-reports-by-lab-assistant'),
    path('lab-reports/delete/<int:report_id>/', LabReportDeleteAPIView.as_view(), name='lab-report-delete'),

    path('birth-report/', BirthRecordCreateView.as_view(), name='birth-record-create'),
    path('birth-report/list/', BirthRecordCreateView.as_view(), name='birth-record-list'),
    path('death-report/', DeathReportCreateView.as_view(), name='create-death-report'),
    path('death-report/list/', DeathReportCreateView.as_view(), name='list-death-report'),

    path('dashboard-stats/', HospitalDashboardStatsAPIView.as_view(), name="hospital-dashboard-stats"),

]
