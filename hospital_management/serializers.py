import base64, uuid
from django.core.files.base import ContentFile
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
import random
from datetime import date
from .models import DoctorsList, Hospital, HospitalContactUs, HospitalDynamicContent, HospitalJobOpenings, HospitalWhyChooseSection, OPDServiceData, OurSpecialities, PatientDetails, Findings, HMSUser, Allergies, PatientFamilyHistory, PatientPastHospitalHistory, MedicalHistoryCurrentHospital, Diseases, OngoingMedication, Medicine, ClinicalNotes, Certificate, Attachments, OPD, PrescriptionItem, Prescription, BillPerticulars, Bill, Invoice, Bed, Ward, IPD, DoctorHistory, Supplier, PharmacyBill, PharmacyMedicine, MedicineStock, StockTransaction, PatientAppointment, DoctorTimetable, LabReport, DeathReport, BirthRecord, DoctorProfile, PharmacyOutBill, InvoicePharmacyBill, PharmacyOutInvoice


class HospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = ['id', 'hospital_id', 'name', 'address', 'owner', 'contact', 'logo']

class HMSUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = HMSUser
        fields = ['id', 'name', 'designation', 'email', 'password','is_active', 'hospital','pharmacist_type', 'is_doctor_available']
        extra_kwargs = {
            'password': {'write_only': True},
            'hospital': {'read_only': True} 
        }
    def validate(self, attrs):
        designation = attrs.get('designation')
        pharmacist_type = attrs.get('pharmacist_type')
        is_doctor_available = attrs.get('is_doctor_available')

        if designation != 'pharmacist' and pharmacist_type:
            raise serializers.ValidationError("Pharmacist type can only be set if designation is 'pharmacist'.")

        if designation == 'pharmacist' and not pharmacist_type:
            attrs['pharmacist_type'] = 'out'

         # Doctor availability validation
        if designation != 'doctor' and 'is_doctor_available' in attrs:
            attrs.pop('is_doctor_available', None)  # Remove it if not doctor

        return attrs
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)

        if instance.designation != 'pharmacist':
            rep.pop('pharmacist_type', None)
        if instance.designation != 'doctor':
            rep.pop('is_doctor_available', None)
        return rep


    def create(self, validated_data):
        # Hash password before saving
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
    

class DoctorProfileSerializer(serializers.ModelSerializer):
    doctor = HMSUserSerializer(read_only=True)

    class Meta:
        model = DoctorProfile
        fields = '__all__'
        read_only_fields = ['hospital']

class AllergiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergies
        fields = ['id', 'name', 'description','hospital']

class PatientDetailsSerializer(serializers.ModelSerializer):
    known_allergies = AllergiesSerializer(many=True, read_only=True)
    # known_allergies_ids = serializers.PrimaryKeyRelatedField(
    #     many=True,
    #     write_only=True,
    #     queryset=Allergies.objects.all(),
    #     source='known_allergies'  # links directly to model field
    # )
    age = serializers.SerializerMethodField()

    class Meta:
        model = PatientDetails
        fields = '__all__'  # includes dynamically calculated 'age'
        read_only_fields = ['patient_id']

    def get_age(self, obj):
        if obj.dob:
            today = date.today()
            return today.year - obj.dob.year - ((today.month, today.day) < (obj.dob.month, obj.dob.day))
        return None
    

class PatientRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientDetails
        fields = [
            'full_name', 'gender', 'dob', 'relative_name',
            'contact_number', 'email', 'address', 'blood_group',
            'medical_history', 'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        patient = PatientDetails(**validated_data)
        patient.set_password(password)

        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        patient.email_otp = otp
        patient.save()

        # Log OTP (Replace with actual email/SMS in production)
        print(f"OTP sent to {patient.email}: {otp}")

        return patient

class FindingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Findings
        fields = '__all__'

class PatientFamilyHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientFamilyHistory
        fields = '__all__'


class PatientPastHospitalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientPastHospitalHistory
        fields = '__all__'

class MedicalHistoryCurrentHospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalHistoryCurrentHospital
        fields = '__all__'


class DiseasesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diseases
        fields = '__all__'


class OngoingMedicationSerializer(serializers.ModelSerializer):
    dosage = serializers.SerializerMethodField()

    class Meta:
        model = OngoingMedication
        fields = '__all__'

    def get_dosage(self, obj):
        if obj.dosage_amount and obj.dosage_unit:
            return f"{obj.dosage_amount}{obj.dosage_unit}"
        return None
    

    # class Meta:
    #     model = OngoingMedication
    #     fields = [
    #         'id',
    #         'medicine_name',
    #         'type',
    #         'dosage',              # combined field like "50mg"
    #         'frequency',
    #         'doctor',
    #         'patient',
    #         'diseases_name',
    #         'notes',
    #         'start_date',
    #     ]

class PharmacyMedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = PharmacyMedicine
        fields = '__all__'
        read_only_fields = ['hospital']


class MedicineSerializer(serializers.ModelSerializer):
    dosage = serializers.SerializerMethodField()
    pharmacy_medicine_detail = PharmacyMedicineSerializer(source='pharmacy_medicine', read_only=True)

    # pharmacy_medicine = serializers.SerializerMethodField()

    class Meta:
        model = Medicine
        fields = [
            'id', 'pharmacy_medicine','pharmacy_medicine_detail', 'dosage', 'dosage_amount',
            'dosage_unit', 'frequency', 'till_date', 'added_by', 'clinical_note', 'hospital',
        ]

    def get_dosage(self, obj):
        return f"{obj.dosage_amount}{obj.dosage_unit}"
    

class ClinicalNotesSerializer(serializers.ModelSerializer):
    medicines = MedicineSerializer(many=True, read_only=True)  # from related_name="medicines"

    class Meta:
        model = ClinicalNotes
        fields = '__all__'


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ['id', 'patient', 'added_by', 'date', 'description', 'remark', 'hospital']
        read_only_fields = ['date'] 

# for get all details api 
class PatientFullHistorySerializer(serializers.Serializer):
    patient = PatientDetailsSerializer()
    allergies = AllergiesSerializer(many=True)
    family_history = PatientFamilyHistorySerializer(many=True)
    past_hospital_history = PatientPastHospitalHistorySerializer(many=True)
    current_hospital_history = MedicalHistoryCurrentHospitalSerializer(many=True)
    diseases = DiseasesSerializer(many=True)
    ongoing_medications = OngoingMedicationSerializer(many=True)


class AttachmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachments
        fields = ['id', 'patient', 'attachment_name', 'description', 'file', 'date', 'hospital']
        read_only_fields = ['date']

class OPDSerializer(serializers.ModelSerializer):
    patient = PatientDetailsSerializer(read_only=True)
    class Meta:
        model = OPD
        fields = '__all__'


class PrescriptionItemSerializer(serializers.ModelSerializer):
    selling_price = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    pharmacy_medicine = PharmacyMedicineSerializer(read_only=True)
    
    class Meta:
        model = PrescriptionItem
        # fields = '__all__'
        fields = [
            'id',
            'pharmacy_medicine', 
            'dosage',
            'duration_days',
            'instruction',
            'quantity',
            'selling_price',
            'total_price',
        ]

    def get_selling_price(self, obj):
        try:
            stock = MedicineStock.objects.filter(
                medicine=obj.pharmacy_medicine, 
                hospital=obj.hospital
            ).order_by('-last_updated').first()  # Or your criteria
            return stock.selling_price if stock else None
        except Exception:
            return None
        
    def get_total_price(self, obj):
        selling_price = self.get_selling_price(obj)
        return round(selling_price * obj.quantity, 2) if selling_price and obj.quantity else None


class PrescriptionSerializer(serializers.ModelSerializer):
    items = PrescriptionItemSerializer(many=True, read_only=True)
    patient = PatientDetailsSerializer(read_only=True)
    
    class Meta:
        model = Prescription
        fields = '__all__'

class BillPerticularsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillPerticulars
        fields = ['id', 'name', 'amount', 'description', 'date_time', 'bill', 'type','hospital']


class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        # fields = ['id', 'date', 'amount', 'patient', 'status', 'payment_mode', 'payment_date_time', 'paid_amount', 'hospital']
        fields = '__all__'

class InvoiceSerializer(serializers.ModelSerializer):
    bill = BillSerializer(read_only=True)
    patient = PatientDetailsSerializer(read_only=True)
    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ['id', 'date']
        

class BedSerializer(serializers.ModelSerializer):
    # patient = serializers.PrimaryKeyRelatedField(queryset=PatientDetails.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Bed
        fields = '__all__'
        read_only_fields = ['hospital']

class WardSerializer(serializers.ModelSerializer):
    beds = BedSerializer(many=True, read_only=True)
    class Meta:
        model = Ward
        fields = '__all__'
        read_only_fields = ['hospital']

class DoctorHistorySerializer(serializers.ModelSerializer):
    # doctor_name = serializers.SerializerMethodField()

    class Meta:
        model = DoctorHistory
        fields = '__all__'

    # def get_doctor_name(self, obj):
    #     return obj.doctor.get_full_name() if obj.doctor else None

class IPDSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(
        queryset=PatientDetails.objects.all()
    )
    patient_details = PatientDetailsSerializer(source='patient', read_only=True)
    admitted_doctor = serializers.PrimaryKeyRelatedField(queryset=HMSUser.objects.filter(designation='doctor'), required=False, allow_null=True)
    active_doctor = serializers.PrimaryKeyRelatedField(queryset=HMSUser.objects.filter(designation='doctor'), required=False, allow_null=True)
    transfer_doctor = serializers.PrimaryKeyRelatedField(queryset=HMSUser.objects.filter(designation='doctor'), required=False, allow_null=True)
    bed = serializers.PrimaryKeyRelatedField(queryset=Bed.objects.all(), required=False, allow_null=True)
    doctor_history = DoctorHistorySerializer(many=True, read_only=True)

    class Meta:
        model = IPD
        fields = '__all__'
        read_only_fields = ['hospital', 'entry_date']



class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'
        read_only_fields = ['hospital']

class PharmacyBillSerializer(serializers.ModelSerializer):
    patient = PatientDetailsSerializer(read_only=True)
    class Meta:
        model = PharmacyBill
        fields = '__all__'
        read_only_fields = ['date_issued', 'payment_date', 'total_amount']


class MedicineStockSerializer(serializers.ModelSerializer):
    pharmacy_medicine = PharmacyMedicineSerializer(read_only=True)
    
    class Meta:
        model = MedicineStock
        fields = '__all__'
        read_only_fields = ['hospital', 'last_updated']

class StockTransactionSerializer(serializers.ModelSerializer):
    hospital = serializers.SerializerMethodField()

    class Meta:
        model = StockTransaction
        fields = ['id', 'transaction_type', 'quantity', 'transaction_date', 'notes', 'medicine_stock', 'hospital']

    def get_hospital(self, obj):
        return obj.medicine_stock.hospital.id if obj.medicine_stock and obj.medicine_stock.hospital else None
    
class PatientAppointmentSerializer(serializers.ModelSerializer):
    preferred_doctor = HMSUserSerializer(read_only=True)
    patient = PatientDetailsSerializer(read_only=True)

    class Meta:
        model = PatientAppointment
        fields = '__all__'
        read_only_fields = ['hospital','final_status', 'created_at', 'updated_at', 'final_time', 'status']
    
class AppointmentStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientAppointment
        fields = ['status', 'final_time', 'status_remark', 'patient_status']

    def validate(self, attrs):
        instance = self.instance  # current appointment object from DB
        new_status = attrs.get('status')

        if new_status == 'cancelled':
            return attrs

        # Prevent updating status if already accepted or rejected
        if instance.status in ['accepted', 'rejected']:
            raise serializers.ValidationError(
                f"Appointment is already '{instance.status}' and cannot be changed."
            )

        # Validate final_time requirement
        if new_status in ['accepted', 'rescheduled'] and not attrs.get('final_time'):
            raise serializers.ValidationError(
                f"'final_time' is required when status is '{new_status}'."
            )

        return attrs
    
    
class PatientAppointmentResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientAppointment
        fields = ['patient_status']

    def validate(self, attrs):
        patient_status = attrs.get('patient_status')
        appointment = self.instance

        if appointment.status != 'rescheduled':
            raise serializers.ValidationError("Patient can only respond to rescheduled appointments.")

        return attrs
    
class DoctorTimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorTimetable
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class LabReportSerializer(serializers.ModelSerializer):
    patient = PatientDetailsSerializer(read_only=True)
    uploaded_by = HMSUserSerializer(read_only=True)

    class Meta:
        model = LabReport
        fields = '__all__'
        read_only_fields = ['hospital']

class BirthRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BirthRecord
        fields = '__all__'
        
class DeathReportSerializer(serializers.ModelSerializer):
    # This will show patient details in GET
    patient = PatientDetailsSerializer(read_only=True)

    # This will accept patient id in POST/PUT
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=PatientDetails.objects.all(), write_only=True, source="patient"
    )
    
    class Meta:
        model = DeathReport
        fields = '__all__'

class PharmacyOutBillSerializer(serializers.ModelSerializer):
    class Meta:
        model = PharmacyOutBill
        fields = [
            'id',
            'hospital',
            'patient_name',
            'note',
            'medicine_items',
            'total_amount',
            'payment_status',
            'payment_mode',
            'payment_date',
            'created_at'
        ]
        read_only_fields = ['created_at', 'hospital']

class PharmacyOutInvoiceSerializer(serializers.ModelSerializer):
    bill = PharmacyOutBillSerializer(read_only=True)
    class Meta:
        model = PharmacyOutInvoice
        fields = '__all__'

class InvoicePharmacyBillSerializer(serializers.ModelSerializer):
    patient = PatientDetailsSerializer(read_only=True)
    bill = PharmacyBillSerializer(read_only=True)
    class Meta:
        model = InvoicePharmacyBill
        # fields = "__all__"
        fields = ['id', 'patient', 'bill', 'date', 'payment_mode', 'paid_amount', 'medical_items']


class Base64FileField(serializers.FileField):
    """
    A Django REST framework field for handling file uploads through raw post data.
    It handles base64-encoded files.
    """

    def to_internal_value(self, data):
        # Check if this is a base64 string
        if isinstance(data, str) and data.startswith("data:"):
            # Format: data:<mime>;base64,<data>
            format, file_str = data.split(';base64,')  
            ext = format.split('/')[-1]  # file extension from mime type

            # Generate file name
            file_name = str(uuid.uuid4())[:12]  # 12 characters are enough
            complete_file_name = f"{file_name}.{ext}"

            # Decode file
            decoded_file = base64.b64decode(file_str)

            data = ContentFile(decoded_file, name=complete_file_name)

        return super().to_internal_value(data)



class HospitalDynamicContentSerializer(serializers.ModelSerializer):
    logo = Base64FileField(max_length=None, use_url=True, required=False)
    image_1 = Base64FileField(max_length=None, use_url=True, required=False)
    image_2 = Base64FileField(max_length=None, use_url=True, required=False)
    image_3 = Base64FileField(max_length=None, use_url=True, required=False)
    main_section_img = Base64FileField(max_length=None, use_url=True, required=False)

    class Meta:
        model = HospitalDynamicContent
        fields = [
            'hospital',
            'header_name', 'header_description', 'logo',
            'hero_name', 'hero_description',
            'image_1', 'image_2', 'image_3',
            'main_title', 'main_description', 'number_1', 'label_1', 'number_2', 'label_2', 'number_3', 'label_3', 'number_4', 'label_4', 'main_section_img',
            'title_color', 'theme_color_1', 'theme_color_2',
            'phone', 'email', 'address'
        ]
        extra_kwargs = {
            'hospital': {'required': True}  # only hospital is mandatory
        }


class OPDServiceContentSerializer(serializers.ModelSerializer):
    emoji = Base64FileField(max_length=None, use_url=True, required=False)

    class Meta:
        model = OPDServiceData
        fields = [
            'id',
            'hospital',
            'service', 'description', 'emoji'
        ]
        extra_kwargs = {
            'hospital': {'required': True}  # only hospital is mandatory
        }

class HospitalWhyChooseSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalWhyChooseSection
        fields = [
            'id',
            'hospital',
            'title', 'description'
        ]
        extra_kwargs = {
            'hospital': {'required': True}  # only hospital is mandatory
        }

class DoctorsListSerializer(serializers.ModelSerializer):
    profile_img = Base64FileField(max_length=None, use_url=True, required=False)

    class Meta:
        model = DoctorsList
        fields = [
            'id',
            'hospital',
            'doctor_name',
            'specialization',
            'description',
            'profile_img'
        ]
        extra_kwargs = {
            'hospital': {'required': True}  # only hospital is mandatory
        }

class OurSpecialitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = OurSpecialities
        fields = [
            'id',
            'hospital',
            'specialization',
            'description',
        ]
        extra_kwargs = {
            'hospital': {'required': True}  # only hospital is mandatory
        }

class HospitalContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalContactUs
        fields = [
            'id',
            'hospital',
            'name',
            'email',
            'message',
            'date'
        ]
        extra_kwargs = {
            'hospital': {'required': True}  # only hospital is mandatory
        }

class HospitalJobOpeningsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HospitalJobOpenings
        fields = [
            'id',
            'hospital',
            'job_name',
            'department',
            'location',
            'status'
        ]
        extra_kwargs = {
            'hospital': {'required': True}  # only hospital is mandatory
        }