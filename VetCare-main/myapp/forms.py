from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Owner, Pet, Vet, Appointment, Medicine, MedicalRecord
class OwnerForm(forms.ModelForm):
    address_1 = forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={'class': 'form-control mb-1', 'placeholder': 'ที่อยู่บรรทัดที่ 1 (บ้านเลขที่, ซอย, ถนน)', 'rows': 1}))
    address_2 = forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'ที่อยู่บรรทัดที่ 2 (ตำบล, อำเภอ, จังหวัด, รหัสไปรษณีย์)', 'rows': 1}))
    class Meta:
        model = Owner
        fields = ['customer_id', 'first_name', 'last_name', 'phone']
        labels = {
            'customer_id': 'รหัสลูกค้า (Customer ID)',
            'first_name': 'ชื่อ (First Name)',
            'last_name': 'นามสกุล (Last Name)',
            'phone': 'เบอร์มือถือ (Mobile)',
        }
        widgets = {
            'customer_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'สร้างอัตโนมัติเมื่อบันทึก', 'readonly': 'readonly'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'กรอกชื่อ'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'กรอกนามสกุล'}),
            'phone': forms.TextInput(attrs={'type': 'tel', 'class': 'form-control', 'placeholder': 'ระบุเบอร์โทรศัพท์ 10 หลัก', 'maxlength': '10', 'oninput': "this.value = this.value.replace(/[^0-9]/g, '').slice(0, 10)"}),
        }
class ClientProfileForm(forms.ModelForm):
    address_1 = forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={'class': 'form-control mb-1', 'placeholder': 'ที่อยู่บรรทัดที่ 1 (บ้านเลขที่, ซอย, ถนน)', 'rows': 1}))
    address_2 = forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'ที่อยู่บรรทัดที่ 2 (ตำบล, อำเภอ, จังหวัด, รหัสไปรษณีย์)', 'rows': 1}))
    class Meta:
        model = Owner
        fields = ['first_name', 'last_name', 'phone']
        labels = {
            'first_name': 'ชื่อ (First Name)',
            'last_name': 'นามสกุล (Last Name)',
            'phone': 'เบอร์มือถือ (Mobile)',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'กรอกชื่อ'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'กรอกนามสกุล'}),
            'phone': forms.TextInput(attrs={'type': 'tel', 'class': 'form-control', 'placeholder': 'ระบุเบอร์โทรศัพท์ 10 หลัก', 'maxlength': '10', 'oninput': "this.value = this.value.replace(/[^0-9]/g, '').slice(0, 10)"}),
        }
class VetForm(forms.ModelForm):
    class Meta:
        model = Vet
        fields = [
            'doctor_id', 'license_no', 'role_level',
            'first_name', 'last_name', 'national_id',
            'specialization', 'degree', 'university', 'license_expiry',
            'address_1', 'address_2', 'phone', 'email',
            'working_hours', 'remarks', 'image'
        ]
        widgets = {
            'doctor_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'สร้างอัตโนมัติเมื่อบันทึก', 'readonly': 'readonly'}),
            'license_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'เลขที่ใบอนุญาต'}),
            'role_level': forms.Select(attrs={'class': 'form-select'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่อ'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'นามสกุล'}),
            'national_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'เลขประจำตัวประชาชน'}),
            'specialization': forms.Select(attrs={'class': 'form-select'}),
            'degree': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'วุฒิการศึกษา'}),
            'university': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'มหาวิทยาลัย'}),
            'license_expiry': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'address_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ที่อยู่บรรทัดที่ 1 (บ้านเลขที่, ซอย, ถนน)'}),
            'address_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ที่อยู่บรรทัดที่ 2 (ตำบล, อำเภอ, จังหวัด, รหัสไปรษณีย์)'}),
            'phone': forms.TextInput(attrs={'type': 'tel', 'class': 'form-control', 'placeholder': 'ระบุเบอร์โทรศัพท์ 10 หลัก', 'maxlength': '10', 'oninput': "this.value = this.value.replace(/[^0-9]/g, '').slice(0, 10)"}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'อีเมล'}),
            'working_hours': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'เช่น จ-ศ 08:00-17:00', 'rows': 3}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'หมายเหตุ', 'rows': 2}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
class PetForm(forms.ModelForm):
    owner_first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'กรอกชื่อ'}))
    owner_last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'กรอกนามสกุล'}))
    owner_address_1 = forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={'class': 'form-control mb-1', 'placeholder': 'ที่อยู่บรรทัดที่ 1 (บ้านเลขที่, ซอย, ถนน)', 'rows': 1}))
    owner_address_2 = forms.CharField(max_length=255, required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'ที่อยู่บรรทัดที่ 2 (ตำบล, อำเภอ, จังหวัด, รหัสไปรษณีย์)', 'rows': 1}))
    owner_phone = forms.CharField(max_length=15, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'เบอร์มือถือ'}))
    owner_email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'อีเมลสำหรับเข้าสู่ระบบ'}))
    owner_password = forms.CharField(max_length=128, required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'กำหนดรหัสผ่านเบื้องต้น'}))
    owner_password_confirm = forms.CharField(max_length=128, required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'ยืนยันรหัสผ่านอีกครั้ง'}))
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # If updating, don't force password/email fields if they are already set or optional
            self.fields['owner_email'].required = False
            self.fields['owner_password'].required = False
            self.fields['owner_password_confirm'].required = False
            # Also make owner name optional if we want to allow updating just pet info
            self.fields['owner_first_name'].required = False
            self.fields['owner_last_name'].required = False
            self.fields['owner_phone'].required = False

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("owner_password")
        confirm = cleaned_data.get("owner_password_confirm")
        if password or confirm:
            if password != confirm:
                self.add_error('owner_password_confirm', "รหัสผ่านที่ยืนยันไม่ตรงกัน")
        return cleaned_data
    species = forms.ChoiceField(
        choices=[
            ('', '--- เลือกประเภทสัตว์ ---'),
            ('สุนัข', 'สุนัข (Dog)'),
            ('แมว', 'แมว (Cat)'),
            ('กระต่าย', 'กระต่าย (Rabbit)'),
            ('นก', 'นก (Bird)'),
            ('หนู', 'หนู (Rodent)'),
            ('สัตว์เลื้อยคลาน', 'สัตว์เลื้อยคลาน (Exotic/Reptile)'),
            ('อื่นๆ', 'อื่นๆ (Other)')
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    class Meta:
        model = Pet
        fields = [
            'name', 'customer_id', 'microchip_number',
            'price_level', 'sex', 'species', 'breed',
            'remarks', 'image', 'birth_date'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่อสัตว์เลี้ยง'}),
            'customer_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'สร้างอัตโนมัติเมื่อบันทึก', 'readonly': 'readonly'}),
            'microchip_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'สร้างอัตโนมัติเมื่อบันทึก', 'readonly': 'readonly'}),
            'price_level': forms.Select(attrs={'class': 'form-select'}),
            'sex': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'breed': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'สายพันธุ์'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'หมายเหตุ', 'rows': 2}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'วันเกิด'
            }),
        }
class ClientPetRegistrationForm(PetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        owner_fields = [
            'owner_first_name', 'owner_last_name', 'owner_address_1',
            'owner_address_2', 'owner_phone', 'owner_email',
            'owner_password', 'owner_password_confirm'
        ]
        for field in owner_fields:
            if field in self.fields:
                self.fields[field].required = False
class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['pet', 'vet', 'appointment_date', 'appointment_time', 'service_type', 'status', 'reason']
        widgets = {
            'pet': forms.Select(attrs={'class': 'form-select', 'id': 'id_pet'}),
            'vet': forms.Select(attrs={'class': 'form-select'}),
            'appointment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'placeholder': 'เลือกวันที่...'}),
            'appointment_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time', 'placeholder': 'เลือกเวลา...'}),
            'service_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'อาการเบื้องต้น หรือสิ่งที่เจ้าของฝากไว้', 'rows': 4}),
        }
class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = [
            'product_id', 'barcode', 'name', 'generic_name', 'product_type', 'unit',
            'cost_price', 'selling_price', 'member_price', 'vat',
            'stock', 'reorder_point', 'supplier', 'expiry_date',
            'description', 'full_description', 'image'
        ]
        widgets = {
            'product_id':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'รหัสสินค้า'}),
            'barcode':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Barcode'}),
            'name':          forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่อยา/เวชภัณฑ์'}),
            'generic_name':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่อสามัญทางยา'}),
            'product_type':  forms.Select(attrs={'class': 'form-select'}),
            'unit':          forms.Select(attrs={'class': 'form-select'}),
            'cost_price':    forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'member_price':  forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'vat':           forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '7.00', 'step': '0.01'}),
            'stock':         forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}),
            'reorder_point': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '10'}),
            'supplier':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ชื่อบริษัท/ผู้จำหน่าย'}),
            'expiry_date':   forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description':      forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'เช่น เก็บในอุณหภูมิต่ำกว่า 25 องศา', 'rows': 2}),
            'full_description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'ใส่รายละเอียด สรรพคุณ และวิธีใช้โดยละเอียด...', 'rows': 4}),
            'image':            forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = [
            'pet', 'vet', 'visit_date', 'visit_type', 'weight', 'temperature',
            'symptoms', 'diagnosis', 'treatment', 'medicines', 'cost',
            'next_visit', 'notes'
        ]
        widgets = {
            'pet': forms.Select(attrs={'class': 'form-select'}),
            'vet': forms.Select(attrs={'class': 'form-select'}),
            'visit_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'visit_type': forms.Select(attrs={'class': 'form-select'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'temperature': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.0', 'step': '0.1'}),
            'symptoms': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'อาการที่พบอย่างละเอียด', 'rows': 2}),
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'การวินิจฉัยโรค', 'rows': 2}),
            'treatment': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'แผนการรักษาและขั้นตอน', 'rows': 3}),
            'medicines': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'next_visit': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'หมายเหตุเพิ่มเติม', 'rows': 2}),
        }
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'อีเมล'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ชื่อจริง'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'นามสกุล'
        })
    )
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'รหัสผ่าน'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'ยืนยันรหัสผ่าน'
        })
        self.fields['password1'].help_text = 'รหัสผ่านต้องมีความยาว 8 ตัวขึ้นไป'
        self.fields['password2'].help_text = ''
        for field in self.fields.values():
            field.error_messages.update({
                'required': 'กรุณากรอกข้อมูลในช่องนี้',
                'invalid': 'ข้อมูลที่กรอกไม่ถูกต้อง'
            })
        self.error_messages.update({
            'password_mismatch': 'รหัสผ่านทั้งสองช่องไม่ตรงกัน กรุณาพิมพ์ใหม่'
        })
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('อีเมลนี้ถูกใช้งานแล้ว')
        return email
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user
class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'อีเมล',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'รหัสผ่าน'
        })
    )