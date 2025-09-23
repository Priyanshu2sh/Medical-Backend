from django.contrib import admin

from .models import DoctorsList, DoctorProfile, Hospital, HospitalDynamicContent, HospitalWhyChooseSection, OPDServiceData, BillPerticulars, Bill, PatientDetails

# Register your models here.
admin.site.register(Hospital)
admin.site.register(HospitalDynamicContent)
admin.site.register(OPDServiceData)
admin.site.register(HospitalWhyChooseSection)
admin.site.register(DoctorsList)
admin.site.register(DoctorProfile)
admin.site.register(BillPerticulars)
admin.site.register(Bill)
admin.site.register(PatientDetails)
