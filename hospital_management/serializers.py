from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from datetime import date
from .models import Hospital, PatientDetails, Findings, HMSUser, Allergies, PatientFamilyHistory, PatientPastHospitalHistory, MedicalHistoryCurrentHospital, Diseases, OngoingMedication, Medicine, ClinicalNotes, Certificate, Attachments, OPD, PrescriptionItem, Prescription, BillPerticulars, Bill


class HospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = ['id', 'hospital_id', 'name', 'address', 'owner', 'contact']

class HMSUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = HMSUser
        fields = ['id', 'name', 'designation', 'email', 'password','is_active', 'hospital']
        extra_kwargs = {
            'password': {'write_only': True},
            'hospital': {'read_only': True} 
        }

    def create(self, validated_data):
        # Hash password before saving
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

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

class MedicineSerializer(serializers.ModelSerializer):
    dosage = serializers.SerializerMethodField()

    class Meta:
        model = Medicine
        fields = [
            'id', 'medicine_name', 'type', 'dosage', 'dosage_amount',
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
    class Meta:
        model = OPD
        fields = '__all__'


class PrescriptionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionItem
        fields = '__all__'


class PrescriptionSerializer(serializers.ModelSerializer):
    items = PrescriptionItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Prescription
        fields = '__all__'

class BillPerticularsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillPerticulars
        fields = ['id', 'name', 'amount', 'description', 'date_time', 'bill', 'hospital']


class BillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        # fields = ['id', 'date', 'amount', 'patient', 'status', 'payment_mode', 'payment_date_time', 'paid_amount', 'hospital']
        fields = '__all__'
