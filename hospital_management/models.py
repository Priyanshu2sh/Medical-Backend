from django.db import models
from django.db.models import JSONField
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password

# Create your models here.
class Hospital(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    owner = models.CharField(max_length=255)
    contact = models.CharField(max_length=15)
    hospital_id = models.CharField(max_length=10, unique=True, blank=True)  # Custom ID like HID00001
    logo = models.ImageField(upload_to='hospital_logos/', null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.hospital_id:
            self.hospital_id = f"HID{self.id:05d}"
            super().save(update_fields=["hospital_id"])

    def __str__(self):
        return self.name


class HMSUser(models.Model):
    DESIGNATION_CHOICES = [
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('receptionist', 'Receptionist'),
        ('pharmacist', 'Pharmacist'),
        ('lab_assistant', 'Lab Assistant'),
        ('admin', 'Admin'),
    ]

    PHARMACIST_TYPE_CHOICES = [
    ('in', 'In'),
    ('out', 'Out'),
    ]

    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name="hms_users", null=True, blank=True)
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=20, choices=DESIGNATION_CHOICES)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # You can store hashed password here
    is_active = models.BooleanField(default=True) 
    pharmacist_type = models.CharField(
        max_length=10,
        choices=PHARMACIST_TYPE_CHOICES,
        null=True,
        blank=True,
        default='out'
    )
    is_doctor_available = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.designation})"

class DoctorProfile(models.Model):
    SPECIALIZATION_CHOICES = [
        ("cardiology", "Cardiology"),
        ("neurology", "Neurology"),
        ("orthopedics", "Orthopedics"),
        ("pediatrics", "Pediatrics"),
        ("gynecology", "Gynecology"),
        ("dermatology", "Dermatology"),
        ("psychiatry", "Psychiatry"),
        ("general_medicine", "General Medicine"),
        ("ent", "ENT"),
        ("other", "Other"),
    ]

    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]

    doctor = models.OneToOneField(HMSUser, on_delete=models.CASCADE, limit_choices_to={'designation': 'doctor'})
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='doctor_profiles')
    phone_number = models.CharField(max_length=15)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    dob = models.DateField()
    photo = models.ImageField(upload_to="doctor_photos/", blank=True, null=True)
    qualification = models.CharField(max_length=255)
    specialization = models.CharField(
        max_length=50, choices=SPECIALIZATION_CHOICES
    )
    experience_years = models.PositiveIntegerField()


    def __str__(self):
        return f"{self.doctor.full_name} - {self.specialization}"

class Allergies(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, null=True, blank=True, related_name="allergies")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    

class PatientDetails(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name="patients", null=True, blank=True)
    patient_id = models.CharField(max_length=7, unique=True, editable=False, null=True, blank=True)
    full_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    dob = models.DateField(null=True, blank=True) 
    relative_name = models.CharField(max_length=100, null=True, blank=True) 
    contact_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)  
    emergency_contact_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField()
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, null=True, blank=True)
    known_allergies = models.ManyToManyField(Allergies,null=True, blank=True)
    medical_history = models.TextField(null=True, blank=True)
    visit_count = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    is_active_patient = models.BooleanField(default=True)

    password = models.CharField(max_length=128, null=True, blank=True)
    email_otp = models.CharField(max_length=6, null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save first to generate `id`
        if not self.patient_id:
            letter = chr(64 + ((self.id - 1) // 99999 + 1))  # A-Z based on id
            number = str(self.id).zfill(5)
            self.patient_id = f"P{letter}{number}"
            super().save(update_fields=['patient_id'])  # Save again to update patient_id

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.full_name
 #Last visite field remaining.

#finding1
class Findings(models.Model):
    hospital = models.ForeignKey('Hospital', on_delete=models.CASCADE, related_name='findings', null=True, blank=True)
    patient = models.ForeignKey('PatientDetails', on_delete=models.CASCADE, related_name='findings')
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)  # Safe now
    note = models.TextField(null=True, blank=True)

    # Vitals
    temperature = models.FloatField(null=True, blank=True)
    pulse = models.IntegerField(null=True, blank=True)
    blood_pressure = models.CharField(max_length=20, null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)

    # Systemic
    cns = models.CharField(max_length=200, null=True, blank=True)
    rs = models.CharField(max_length=200, null=True, blank=True)
    pa = models.CharField(max_length=200, null=True, blank=True)
    wbc = models.CharField(max_length=100, null=True, blank=True)
    rbc = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Findings of {self.patient.full_name}"
    

class PatientFamilyHistory(models.Model):
    hospital = models.ForeignKey('Hospital', on_delete=models.CASCADE, related_name='family_histories', null=True, blank=True)
    patient = models.ForeignKey(PatientDetails, on_delete=models.CASCADE, related_name='family_history')
    relation = models.CharField(max_length=50)  # e.g., Father, Mother, etc.
    name = models.CharField(max_length=100)
    disease = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    period = models.TextField()  # e.g., "2010-2015", "Since childhood", etc.

    def __str__(self):
        return f"{self.name} ({self.relation}) - {self.disease}"
    

class PatientPastHospitalHistory(models.Model):
    hospital = models.ForeignKey('Hospital', on_delete=models.CASCADE, related_name='past_patient_histories', null=True, blank=True)
    patient = models.ForeignKey(PatientDetails, on_delete=models.CASCADE, related_name='past_hospital_history')
    diagnosis_name = models.CharField(max_length=255)
    hospital_name = models.CharField(max_length=255)
    address = models.TextField()
    doctor_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.diagnosis_name} at {self.hospital_name}"
    

class MedicalHistoryCurrentHospital(models.Model):
    hospital = models.ForeignKey('Hospital', on_delete=models.CASCADE, related_name='current_medical_histories', null=True, blank=True)
    diagnosis_name = models.CharField(max_length=255)
    doctor = models.ForeignKey(
        HMSUser,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'designation': 'doctor'},  # ✅ only allow doctors
        related_name='diagnosed_cases'
    )
    patient = models.ForeignKey(PatientDetails, on_delete=models.CASCADE, related_name='current_hospital_history')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.diagnosis_name} by {self.doctor.name if self.doctor else 'Unknown'}"
    

class Diseases(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('recovered', 'Recovered'),
        ('ongoing', 'Ongoing'),
        ('chronic', 'Chronic'),
    ]

    SEVERITY_CHOICES = [
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
        ('critical', 'Critical'),
    ]

    hospital = models.ForeignKey('Hospital', on_delete=models.CASCADE, related_name='diseases', null=True, blank=True)
    patient = models.ForeignKey(PatientDetails, on_delete=models.CASCADE, related_name='diseases')
    disease_name = models.CharField(max_length=255)
    diagnosis_date = models.DateTimeField(auto_now_add=True)
    severity = models.CharField(max_length=50, choices=SEVERITY_CHOICES, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return f"{self.disease_name} ({self.status})"
    


class OngoingMedication(models.Model):
    MEDICINE_TYPE_CHOICES = [
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('syrup', 'Syrup'),
        ('injection', 'Injection'),
        ('ointment', 'Ointment'),
        ('inhaler', 'Inhaler'),
        ('drops', 'Drops'),
        ('patch', 'Patch'),
    ]

    DOSAGE_UNIT_CHOICES = [
        ('mg', 'mg'),
        ('ml', 'ml'),
        ('g', 'g'),
        ('mcg', 'mcg'),
        ('units', 'units'),
    ]

    FREQUENCY_CHOICES = [
        ('once_daily', 'Once daily'),
        ('twice_daily', 'Twice daily'),
        ('thrice_daily', 'Thrice daily'),
        ('once_evening', 'Once in the evening'),
        ('once_morning', 'Once in the morning'),
        ('alternate_days', 'Alternate days'),
        ('weekly', 'Weekly'),
        ('as_needed', 'As needed (PRN)'),
        ('custom', 'Custom (Specify in notes)'),
    ]

    hospital = models.ForeignKey('Hospital', on_delete=models.CASCADE, related_name='ongoing_medications', null=True, blank=True)
    medicine_name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=MEDICINE_TYPE_CHOICES)
    dosage_amount = models.FloatField(null=True, blank=True)  # user will enter like 50
    dosage_unit = models.CharField(max_length=10, choices=DOSAGE_UNIT_CHOICES)
    frequency = models.CharField(max_length=50, choices=FREQUENCY_CHOICES)
    doctor = models.ForeignKey('HMSUser', on_delete=models.SET_NULL, null=True, limit_choices_to={'designation': 'doctor'})
    patient = models.ForeignKey('PatientDetails', on_delete=models.CASCADE, related_name='ongoing_medications')
    diseases_name = models.ForeignKey('Diseases', on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)  # optional notes field
    start_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.medicine_name} for {self.patient.full_name}"


class ClinicalNotes(models.Model):
    PAIN_SEVERITY_CHOICES = [
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
        ('unbearable', 'Unbearable'),
    ]

    added_by = models.ForeignKey(
        'HMSUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='clinical_notes_added'
    )
    hospital = models.ForeignKey('Hospital', on_delete=models.CASCADE, related_name='clinical_notes', null=True, blank=True)
    patient = models.ForeignKey(PatientDetails, on_delete=models.CASCADE)
    pain = models.CharField(max_length=255, null=True, blank=True)
    pain_start_date = models.DateField(null=True, blank=True)
    pain_severity = models.CharField(
        max_length=50, choices=PAIN_SEVERITY_CHOICES, null=True, blank=True
    )
    observation = models.TextField()
    diagnosis = models.TextField()
    evidence = models.TextField()
    treatment_plan = models.TextField()
    advice = models.TextField()
    remark = models.TextField()
    next_followup_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Clinical Notes for {self.patient} on {self.created_at.date()}"
    

class PharmacyMedicine(models.Model):
    TYPE_CHOICES = [
        ('tablet', 'Tablet'),
        ('liquid', 'Liquid'),
        ('injection', 'Injection'),
        ('ointment', 'Ointment'),
        ('inhaler', 'Inhaler'),
        ('drops', 'Drops'),
    ]

    DOSAGE_UNIT_CHOICES = [
        ('mg', 'mg'),
        ('ml', 'ml'),
        ('g', 'g'),
        ('units', 'units'),
    ]
    hospital = models.ForeignKey('Hospital', on_delete=models.CASCADE, related_name='pharmacy_medicines', null=True, blank=True)
    medicine_name = models.CharField(max_length=100)
    medicine_type = models.CharField(max_length=20, choices=TYPE_CHOICES) # e.g. Tablet, Syrup
    medicine_unit = models.CharField(max_length=10, choices=DOSAGE_UNIT_CHOICES)  # e.g. mg, ml
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    is_narcotic = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.medicine_name}"

class Medicine(models.Model):
    TYPE_CHOICES = [
        ('tablet', 'Tablet'),
        ('liquid', 'Liquid'),
        ('injection', 'Injection'),
        ('ointment', 'Ointment'),
        ('inhaler', 'Inhaler'),
        ('drops', 'Drops'),
    ]

    DOSAGE_UNIT_CHOICES = [
        ('mg', 'mg'),
        ('ml', 'ml'),
        ('g', 'g'),
        ('units', 'units'),
    ]

    FREQUENCY_CHOICES = [
        ('once_daily', 'Once Daily'),
        ('twice_daily', 'Twice Daily'),
        ('thrice_daily', 'Thrice Daily'),
        ('morning', 'Morning'),
        ('evening', 'Evening'),
        ('night', 'Night'),
        ('before_meal', 'Before Meal'),
        ('after_meal', 'After Meal'),
    ]
    
    hospital = models.ForeignKey('Hospital', on_delete=models.CASCADE, related_name='medicines', null=True, blank=True)
    
    pharmacy_medicine = models.ForeignKey(
        'PharmacyMedicine',
        on_delete=models.CASCADE,
        related_name='prescribed_medicines'
    )
    dosage_amount = models.PositiveIntegerField()
    dosage_unit = models.CharField(max_length=10, choices=DOSAGE_UNIT_CHOICES)
    frequency = models.CharField(max_length=30, choices=FREQUENCY_CHOICES)
    till_date = models.DateField(null=True, blank=True)

    added_by = models.ForeignKey(
        HMSUser, on_delete=models.SET_NULL, null=True,
        limit_choices_to={'designation': 'doctor'}
    )
    clinical_note = models.ForeignKey(
        ClinicalNotes, on_delete=models.CASCADE, related_name='medicines'
    )

    def __str__(self):
        return f"{self.clinical_note.patient}"
    

class Certificate(models.Model):
    hospital = models.ForeignKey('Hospital', on_delete=models.CASCADE, related_name='certificates', null=True, blank=True)
    patient = models.ForeignKey(PatientDetails, on_delete=models.CASCADE, related_name='certificates')
    added_by = models.ForeignKey(
        HMSUser, on_delete=models.SET_NULL, null=True,
        limit_choices_to={'designation': 'doctor'}
    )
    date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    remark = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Certificate for {self.patient.full_name} by {self.added_by.name if self.added_by else 'Unknown'}"

class Attachments(models.Model):
    hospital = models.ForeignKey('Hospital', on_delete=models.CASCADE, related_name='attachments', null=True, blank=True)
    patient = models.ForeignKey(PatientDetails, on_delete=models.CASCADE, related_name='attachments')
    attachment_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='attachments/')
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.attachment_name} - {self.patient.full_name}"
    

class OPD(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('out', 'Out'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
    ]

    OPD_TYPE_CHOICES = [
        ('normal', 'Normal'),
        ('emergency', 'Emergency'),
    ]

    hospital = models.ForeignKey('Hospital', on_delete=models.CASCADE, related_name='opd_records', null=True, blank=True)
    date_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    patient = models.ForeignKey(PatientDetails, on_delete=models.CASCADE, related_name='opd_visits')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    visit_count = models.IntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    doctor = models.ForeignKey(HMSUser, on_delete=models.SET_NULL, null=True, limit_choices_to={'designation': 'doctor'})
    opd_type = models.CharField(
        max_length=20,
        choices=OPD_TYPE_CHOICES,
        default='normal',
        null=True,
        blank=True
    )


    def __str__(self):
        return f"OPD Visit - {self.patient.name} on {self.date_time}"


class Prescription(models.Model):

    patient = models.ForeignKey(PatientDetails, on_delete=models.CASCADE, related_name="prescriptions")
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey('HMSUser', limit_choices_to={'designation': 'doctor'}, on_delete=models.CASCADE)
    date_issued = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)


    def __str__(self):
        return f"Prescription for {self.patient} by {self.user} on {self.date_issued.date()}"


class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name="items")
    hospital = models.ForeignKey('Hospital', on_delete=models.CASCADE, related_name="prescription_items", null=True, blank=True)
    pharmacy_medicine = models.ForeignKey('PharmacyMedicine', on_delete=models.CASCADE, related_name="prescription_items")
    dosage = models.CharField(max_length=100)
    duration_days = models.IntegerField()
    instruction = models.TextField()
    quantity = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.medicine_name

class Supplier(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='suppliers', null=True, blank=True)
    supplier_name = models.CharField(max_length=100)
    contact = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    purchase_date_time = models.DateTimeField(null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.supplier_name

class Bill(models.Model):
    STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid')
    ]

    PAYMENT_MODE_CHOICES = [
        ('cash', 'Cash'),
        ('upi', 'UPI'),
        ('card', 'Card'),
        ('netbanking', 'Net Banking'),
        ('other', 'Other'),
    ]

    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='bills')
    patient = models.ForeignKey(PatientDetails, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unpaid')
    payment_mode = models.CharField(max_length=50,choices=PAYMENT_MODE_CHOICES, null=True, blank=True)
    payment_date_time = models.DateTimeField(null=True, blank=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Bill #{self.id} - {self.patient}"


class BillPerticulars(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='bill_perticulars')
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='bill_perticulars',blank=True, null=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, null=True, blank=True)
    # quantity = models.PositiveIntegerField(default=1)
    amount = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - ₹{self.amount}"


class Invoice(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name="invoices")
    patient = models.ForeignKey(PatientDetails, on_delete=models.CASCADE, related_name="invoices", null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    payment_mode = models.CharField(max_length=20)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    particulars = JSONField(default=list, blank=True) 

    def __str__(self):
        return f"Invoice #{self.id} for Bill #{self.bill.id}"

class Ward(models.Model):
    WARD_TYPE_CHOICES = [
        ('general', 'General'),
        ('icu', 'ICU'),
        ('private', 'Private'),
        ('semi-private', 'Semi-Private'),
    ]

    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='wards')
    ward_name = models.CharField(max_length=100, null=True, blank=True)
    floor = models.IntegerField(null=True, blank=True)
    building = models.CharField(max_length=100, null=True, blank=True)
    ward_type = models.CharField(max_length=50, choices=WARD_TYPE_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"{self.ward_name} - {self.floor} - {self.building}"


class Bed(models.Model):
    BED_TYPE_CHOICES = [
        ('standard', 'Standard'),
        ('electric', 'Electric'),
        ('manual', 'Manual'),
        ('icu', 'ICU'),
        
    ]

    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name="beds", null=True, blank=True)
    ward = models.ForeignKey(Ward, on_delete=models.CASCADE, related_name="beds")
    bed_no = models.CharField(max_length=20)
    patient = models.ForeignKey(PatientDetails, on_delete=models.SET_NULL, null=True, blank=True, related_name="beds")
    occupied_date = models.DateTimeField(null=True, blank=True)
    is_occupied = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    bed_type = models.CharField(max_length=50, choices=BED_TYPE_CHOICES)

    def __str__(self):
        return f"Bed {self.bed_no} in {self.ward.ward_name}"
    
class IPD(models.Model):
    PATIENT_TYPE_CHOICES = [
        ('normal', 'Normal'),
        ('mlc', 'MLC'),
    ]
     
    MLC_TYPE_CHOICES = [
        ('accident', 'Accident'),
        ('assault', 'Assault'),
        ('burn', 'Burn'),
        ('poisoning', 'Poisoning'),
        ('suicide', 'Suicide'),
        ('other', 'Other'),
    ]

    DEPARTMENT_CHOICES = [
        ('operation_theatre', 'Operation Theatre'),
        ('general_surgery', 'General Surgery'),
        ('casualty_department', 'Casualty Department'),
        ('ent_department', 'ENT Department'),
        ('genecology_department', 'Genecology Department'),
        ('neurology_department', 'Neurology Department'),
        ('psychiatry_department', 'Psychiatry Department'),
        ('paediatrics_department', 'Paediatrics Department'),
    ]

    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='ipds')
    patient = models.ForeignKey(PatientDetails, on_delete=models.CASCADE, related_name="ipds")
    admitted_doctor = models.ForeignKey(HMSUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="admitted_ipds")
    active_doctor = models.ForeignKey(HMSUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="active_ipds")
    transfer_doctor = models.ForeignKey(HMSUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="transferred_ipds")

    bill_category = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    department = models.CharField(
        max_length=50,
        choices=DEPARTMENT_CHOICES,
        null=True,
        blank=True
    )
    bed = models.ForeignKey(Bed, on_delete=models.SET_NULL, null=True, blank=True, related_name="ipd_beds")
    entry_date = models.DateTimeField(auto_now_add=True) 
    admit_date = models.DateTimeField(null=True, blank=True)  
    # Patient Type
    patient_type = models.CharField(max_length=10, choices=PATIENT_TYPE_CHOICES, default='normal')
    # Guardian Details
    guardian_relation = models.CharField(max_length=50, null=True, blank=True)
    guardian_name = models.CharField(max_length=100, null=True, blank=True)
    guardian_mobile = models.CharField(max_length=15, null=True, blank=True)
    # MLC Info
    police_station_name = models.CharField(max_length=100, null=True, blank=True)
    informed_on = models.DateField(null=True, blank=True)
    injury_details = models.TextField(null=True, blank=True)
    incident_datetime = models.DateTimeField(null=True, blank=True)
    mlc_number = models.CharField(max_length=50, null=True, blank=True)
    mlc_type = models.CharField(max_length=20, choices=MLC_TYPE_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"IPD #{self.id} for {self.patient.full_name}"


class DoctorHistory(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='doctor_histories', null=True, blank=True)
    ipd = models.ForeignKey(IPD, on_delete=models.CASCADE, related_name='doctor_history', null=True, blank=True)
    doctor = models.ForeignKey(HMSUser, on_delete=models.CASCADE, limit_choices_to={'designation': 'doctor'}, null=True, blank=True)
    from_date = models.DateTimeField(null=True, blank=True)
    till_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Doctor {self.doctor.get_full_name()} (IPD #{self.ipd.id})"

# Pharmacy 
class PharmacyBill(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
    ]

    PAYMENT_MODE_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('netbanking', 'Net Banking'),
    ]

    hospital = models.ForeignKey('Hospital', on_delete=models.CASCADE, related_name='pharmacy_bills')
    patient = models.ForeignKey('PatientDetails', on_delete=models.CASCADE, related_name='pharmacy_bills')
    doctor = models.ForeignKey(HMSUser, on_delete=models.CASCADE, limit_choices_to={'designation': 'doctor'}, null=True, blank=True)
    date_issued = models.DateTimeField(null=True, blank=True)
    prescription = models.ForeignKey(
        'Prescription',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pharmacy_bills'
    )

    medical_items = models.JSONField(null=True, blank=True)  
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES, null=True, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Pharmacy Bill #{self.id} for {self.patient}"
    
# Pharmacy stock 

    
class MedicineStock(models.Model):
    hospital = models.ForeignKey('Hospital', on_delete=models.CASCADE, related_name='medicine_stocks', null=True, blank=True)
    medicine = models.ForeignKey(PharmacyMedicine, on_delete=models.CASCADE, related_name='stocks')
    batch_number = models.CharField(max_length=50)
    expiry_date = models.DateField()
    quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    last_updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.medicine.medicine_name} - {self.batch_number}"
    
class StockTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        # ('RETURN', 'Return'),
        # ('ADJUSTMENT', 'Adjustment'),
    )

    hospital = models.ForeignKey('Hospital', on_delete=models.CASCADE, related_name='stock_transactions', null=True, blank=True)
    medicine_stock = models.ForeignKey(MedicineStock, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=15, choices=TRANSACTION_TYPES)
    quantity = models.PositiveIntegerField()
    transaction_date = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.quantity} units on {self.transaction_date.date()}"

class PatientAppointment(models.Model):
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('accepted', 'Accepted'),
        ('rescheduled', 'Rescheduled'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    PATIENT_STATUS_CHOICES = [
        ('available', 'Available'),
        ('not_available', 'Not Available'),
        ('cancelled', 'Cancelled'),
    ]
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='appointments')
    patient = models.ForeignKey(PatientDetails, on_delete=models.CASCADE, related_name='appointments')
    preferred_doctor = models.ForeignKey(HMSUser, on_delete=models.CASCADE, limit_choices_to={'designation': 'doctor'}, related_name='appointments')
    department = models.CharField(max_length=100)
    reason = models.TextField()
    preferred_date_and_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    status_remark = models.TextField(null=True, blank=True)
    patient_status = models.CharField(max_length=20, choices=PATIENT_STATUS_CHOICES)
    final_time = models.DateTimeField(null=True, blank=True)
    final_status = models.BooleanField(default=False, editable=False) 

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        if self.status == 'accepted':
            self.final_status = True
        elif self.status == 'rescheduled' and self.patient_status == 'available':
            self.final_status = True
        else:
            self.final_status = False

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Appointment with {self.preferred_doctor.name} on {self.preferred_date_and_time.strftime('%Y-%m-%d %H:%M')}"

class DoctorTimetable(models.Model):
    DAYS_OF_WEEK = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    doctor = models.ForeignKey(
        HMSUser, 
        on_delete=models.CASCADE, 
        related_name='timetables',
        limit_choices_to={'designation': 'doctor'}
    )
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='doctor_timetables')
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    date = models.DateField(null=True, blank=True)  # Optional: used for specific exceptions
    start_time = models.TimeField()
    end_time = models.TimeField()
    remark = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['doctor', 'hospital', 'day', 'start_time', 'end_time']

    # def clean(self):
    #     if self.start_time >= self.end_time:
    #         raise ValidationError("Start time must be before end time.")

    #     # Check for overlapping schedules
    #     overlapping = DoctorTimetable.objects.filter(
    #         doctor=self.doctor,
    #         date=self.date,
    #         hospital=self.hospital
    #     ).exclude(pk=self.pk).filter(
    #         start_time__lt=self.end_time,
    #         end_time__gt=self.start_time
    #     )

    #     if overlapping.exists():
    #         raise ValidationError("This time slot overlaps with an existing timetable.")

    # def save(self, *args, **kwargs):
    #     self.clean()
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.doctor.name} - {self.date} ({self.start_time} to {self.end_time})"

    def __str__(self):
        return f"{self.doctor.name} - {self.day} ({self.start_time} to {self.end_time})"
    

# For Lab assistance
class LabReport(models.Model):
    patient = models.ForeignKey(PatientDetails, on_delete=models.CASCADE, related_name='lab_reports')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name="lab_reports")
    uploaded_by = models.ForeignKey(HMSUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_reports')
    report_name = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)
    file = models.FileField(upload_to='lab_reports/')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.report_name} - {self.patient.full_name}"

class BirthRecord(models.Model):
    patient = models.ForeignKey(PatientDetails, on_delete=models.CASCADE, related_name="birth_records")  # mother
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    child_name = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    dob_child = models.DateTimeField()
    birth_place = models.CharField(max_length=255)
    father_name = models.CharField(max_length=100)
    weight = models.DecimalField(max_digits=5, decimal_places=2, help_text="Weight in KG")
    remark = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(HMSUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"BirthRecord of {self.child_name or 'Unnamed'} ({self.dob_child.date()})"
    
class DeathReport(models.Model):
    patient = models.ForeignKey(PatientDetails, on_delete=models.CASCADE, related_name="death_reports")
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    date_of_death = models.DateTimeField()
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    cause_of_death = models.TextField()
    remark = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(HMSUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"DeathReport of {self.patient.full_name} ({self.date_of_death.date()})"

class PharmacyOutBill(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
    ]

    PAYMENT_MODE_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('netbanking', 'Net Banking'),
    ]

    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    patient_name = models.CharField(max_length=255, null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    medicine_items = models.JSONField()  # Stores list of medicines in JSON format
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES, null=True, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Out-Patient Bill - {self.patient_name} ({self.hospital.name})"

class PharmacyOutInvoice(models.Model):
    bill = models.ForeignKey('PharmacyOutBill', on_delete=models.CASCADE, related_name='invoices')
    patient_name = models.CharField(max_length=255)
    date = models.DateTimeField(default=timezone.now)
    payment_mode = models.CharField(max_length=50)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    medicine_items = models.JSONField()

    def __str__(self):
        return f"Invoice #{self.id} - {self.patient_name}"


class InvoicePharmacyBill(models.Model):
    bill = models.ForeignKey('PharmacyBill', on_delete=models.CASCADE, related_name='pharmacy_invoices')
    patient = models.ForeignKey('PatientDetails', on_delete=models.CASCADE, related_name='pharmacy_invoices', null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    payment_mode = models.CharField(max_length=50, blank=True, null=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    medical_items = models.JSONField(default=list)  # Store medicine details in JSON format

    def __str__(self):
        return f"Invoice #{self.id} - {self.patient_name}"
