from django.db import models

# Create your models here.
class Hospital(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    owner = models.CharField(max_length=255)
    contact = models.CharField(max_length=15)
    hospital_id = models.CharField(max_length=10, unique=True, blank=True)  # Custom ID like HID00001

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
        ('admin', 'Admin'),
    ]

    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name="hms_users", null=True, blank=True)
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=20, choices=DESIGNATION_CHOICES)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # You can store hashed password here
    is_active = models.BooleanField(default=True) 

    def __str__(self):
        return f"{self.name} ({self.designation})"

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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save first to generate `id`
        if not self.patient_id:
            letter = chr(64 + ((self.id - 1) // 99999 + 1))  # A-Z based on id
            number = str(self.id).zfill(5)
            self.patient_id = f"P{letter}{number}"
            super().save(update_fields=['patient_id'])  # Save again to update patient_id

    def __str__(self):
        return self.full_name
 #Last visite field remaining.

#finding
class Findings(models.Model):
    hospital = models.ForeignKey('Hospital', on_delete=models.CASCADE, related_name='findings', null=True, blank=True)
    patient = models.ForeignKey('PatientDetails', on_delete=models.CASCADE, related_name='findings')
    date = models.DateField(auto_now_add=True)

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
        return f"Findings of {self.patient.full_name} on {self.date}"
    

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
    medicine_name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
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
        return f"{self.medicine_name} for {self.clinical_note.patient}"
    

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

    hospital = models.ForeignKey('Hospital', on_delete=models.CASCADE, related_name='opd_records', null=True, blank=True)
    date_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    patient = models.ForeignKey(PatientDetails, on_delete=models.CASCADE, related_name='opd_visits')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    visit_count = models.IntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    doctor = models.ForeignKey(HMSUser, on_delete=models.SET_NULL, null=True, limit_choices_to={'designation': 'doctor'})

    def __str__(self):
        return f"OPD Visit - {self.patient.name} on {self.date}"


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
    medicine_name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=100)
    duration_days = models.IntegerField()
    instruction = models.TextField()

    def __str__(self):
        return self.medicine_name


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
    # quantity = models.PositiveIntegerField(default=1)
    amount = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - ₹{self.amount}"