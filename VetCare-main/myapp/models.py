from django.db import models
class Owner(models.Model):
    from django.conf import settings
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='owner_profile', verbose_name='บัญชีผู้ใช้')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    customer_id = models.CharField(max_length=50, blank=True, null=True, verbose_name='รหัสลูกค้า')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        updated = False
        if not self.customer_id:
            self.customer_id = f"OWN{self.pk:06d}"
            updated = True
        if updated:
            Owner.objects.filter(pk=self.pk).update(customer_id=self.customer_id)
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
class Pet(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='pets')
    name = models.CharField(max_length=100)
    customer_id = models.CharField(max_length=50, blank=True, null=True, verbose_name='รหัสลูกค้า')
    microchip_number = models.CharField(max_length=50, blank=True, null=True, verbose_name='เลขที่ชิป')
    price_level_choices = [
        ('ราคาปกติ', 'ราคาปกติ'),
        ('ราคาพิเศษ', 'ราคาพิเศษ')
    ]
    price_level = models.CharField(max_length=50, choices=price_level_choices, blank=True, null=True, verbose_name='ระดับราคา')
    sex_choices = [
        ('M', 'ตัวผู้'),
        ('F', 'ตัวเมีย')
    ]
    sex = models.CharField(max_length=10, choices=sex_choices, blank=True, null=True, verbose_name='เพศ')
    species = models.CharField(max_length=50, verbose_name='ประเภทสัตว์')
    breed = models.CharField(max_length=50, blank=True, null=True, verbose_name='สายพันธุ์')
    remarks = models.TextField(blank=True, null=True, verbose_name='หมายเหตุ')
    image = models.ImageField(upload_to='pet_images/', blank=True, null=True, verbose_name='รูปภาพสัตว์เลี้ยง')
    birth_date = models.DateField(blank=True, null=True, verbose_name='วันเกิด')
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        updated = False
        if not self.customer_id:
            self.customer_id = f"PET{self.pk:06d}"
            updated = True
        if not self.microchip_number:
            self.microchip_number = f"MC{self.pk:06d}"
            updated = True
        if updated:
            Pet.objects.filter(pk=self.pk).update(customer_id=self.customer_id, microchip_number=self.microchip_number)
    def __str__(self):
        return f"{self.name} ({self.species})"

    @property
    def age(self):
        if not self.birth_date:
            return None
        from datetime import date
        today = date.today()
        # Calculate age in years
        age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return age
class Vet(models.Model):
    doctor_id = models.CharField(max_length=50, blank=True, null=True, verbose_name='รหัสแพทย์')
    license_no = models.CharField(max_length=50, blank=True, null=True, verbose_name='เลขที่ใบอนุญาตประกอบวิชาชีพ')
    role_choices = [
        ('แพทย์ฝึกหัด', 'แพทย์ฝึกหัด'),
        ('สัตวแพทย์', 'สัตวแพทย์'),
        ('สัตวแพทย์อาวุโส', 'สัตวแพทย์อาวุโส')
    ]
    role_level = models.CharField(max_length=50, choices=role_choices, blank=True, null=True, verbose_name='ระดับตำแหน่ง')
    first_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='ชื่อ')
    last_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='นามสกุล')
    national_id = models.CharField(max_length=20, blank=True, null=True, verbose_name='เลขประจำตัวประชาชน')
    specialization_choices = [
        ('อายุรกรรมทั่วไป', 'อายุรกรรมทั่วไป'),
        ('ศัลยกรรม', 'ศัลยกรรม'),
        ('สัตว์เลี้ยงพิเศษ (Exotic)', 'สัตว์เลี้ยงพิเศษ (Exotic)'),
        ('โรคผิวหนัง', 'โรคผิวหนัง'),
        ('หัวใจและหลอดเลือด', 'หัวใจและหลอดเลือด'),
        ('จักษุวิทยา', 'จักษุวิทยา')
    ]
    specialization = models.CharField(max_length=100, choices=specialization_choices, blank=True, null=True, verbose_name='สาขาความเชี่ยวชาญ')
    degree = models.CharField(max_length=100, blank=True, null=True, verbose_name='วุฒิการศึกษา')
    university = models.CharField(max_length=100, blank=True, null=True, verbose_name='มหาวิทยาลัย')
    license_expiry = models.DateField(blank=True, null=True, verbose_name='วันหมดอายุใบอนุญาต')
    address_1 = models.CharField(max_length=255, blank=True, null=True, verbose_name='ที่อยู่บรรทัดที่ 1')
    address_2 = models.CharField(max_length=255, blank=True, null=True, verbose_name='ที่อยู่บรรทัดที่ 2')
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name='เบอร์มือถือ')
    email = models.EmailField(blank=True, null=True, verbose_name='อีเมล')
    working_hours = models.TextField(blank=True, null=True, verbose_name='ตารางปฏิบัติงาน')
    remarks = models.TextField(blank=True, null=True, verbose_name='หมายเหตุ')
    image = models.ImageField(upload_to='vet_images/', blank=True, null=True, verbose_name='รูปถ่ายแพทย์')
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        updated = False
        if not self.doctor_id:
            self.doctor_id = f"VET{self.pk:06d}"
            updated = True
        if updated:
            Vet.objects.filter(pk=self.pk).update(doctor_id=self.doctor_id)

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip() if self.first_name or self.last_name else "Unnamed Vet"
class Medicine(models.Model):
    TYPE_CHOICES = [
        ('ยาเม็ด', 'ยาเม็ด'),
        ('ยาน้ำ', 'ยาน้ำ'),
        ('ยาฉีด', 'ยาฉีด'),
        ('วัคซีน', 'วัคซีน'),
        ('อุปกรณ์ทำแผล', 'อุปกรณ์ทำแผล'),
        ('อุปกรณ์การแพทย์', 'อุปกรณ์การแพทย์'),
        ('เวชภัณฑ์', 'เวชภัณฑ์'),
        ('อาหารเสริม', 'อาหารเสริม'),
        ('อื่นๆ', 'อื่นๆ'),
    ]
    UNIT_CHOICES = [
        ('กล่อง', 'กล่อง'),
        ('แผง', 'แผง'),
        ('เม็ด', 'เม็ด'),
        ('ขวด', 'ขวด'),
        ('หลอด', 'หลอด'),
        ('ชิ้น', 'ชิ้น'),
        ('ซอง', 'ซอง'),
        ('ชุด', 'ชุด'),
    ]
    product_id   = models.CharField(max_length=50, blank=True, null=True, verbose_name='รหัสสินค้า')
    barcode      = models.CharField(max_length=100, blank=True, null=True, verbose_name='Barcode')
    name         = models.CharField(max_length=200, verbose_name='ชื่อยา/เวชภัณฑ์')
    generic_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='ชื่อสามัญทางยา')
    product_type = models.CharField(max_length=50, choices=TYPE_CHOICES, blank=True, null=True, verbose_name='ประเภทสินค้า')
    unit         = models.CharField(max_length=20, choices=UNIT_CHOICES, blank=True, null=True, verbose_name='หน่วยนับ')
    cost_price    = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='ราคาทุน')
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='ราคาขาย')
    member_price  = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name='ราคาสมาชิก')
    vat           = models.DecimalField(max_digits=5, decimal_places=2, default=7.0, verbose_name='VAT (%)')
    stock         = models.IntegerField(default=0, verbose_name='จำนวนคงเหลือ')
    reorder_point = models.IntegerField(default=10, verbose_name='จุดสั่งซื้อ (Reorder Point)')
    supplier      = models.CharField(max_length=200, blank=True, null=True, verbose_name='ผู้จำหน่าย/Supplier')
    expiry_date   = models.DateField(blank=True, null=True, verbose_name='วันหมดอายุ')
    description      = models.TextField(blank=True, null=True, verbose_name='หมายเหตุ/วิธีเก็บรักษา')
    full_description = models.TextField(blank=True, null=True, verbose_name='รายละเอียดสินค้าทั้งหมด')
    image            = models.ImageField(upload_to='medicine_images/', blank=True, null=True, verbose_name='รูปสินค้า')
    @property
    def is_low_stock(self):
        return self.stock <= self.reorder_point
    @property
    def days_left(self):
        if not self.expiry_date:
            return None
        from datetime import date
        return (self.expiry_date - date.today()).days
    @property
    def days_left_abs(self):
        val = self.days_left
        return abs(val) if val is not None else None
    @property
    def expiry_status(self):
        from datetime import date
        if not self.expiry_date:
            return 'none'
        today = date.today()
        days_left = (self.expiry_date - today).days
        if days_left <= 7:
            return 'expired'
        elif days_left <= 30:
            return 'soon'
        elif days_left <= 90:
            return 'medium'
        else:
            return 'good'
    def __str__(self):
        return self.name
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending',     'รอยืนยัน'),
        ('confirmed',   'ยืนยันแล้ว'),
        ('in_progress', 'กำลังตรวจ'),
        ('cancelled',   'ยกเลิก'),
        ('completed',   'เสร็จสิ้น'),
    ]
    SERVICE_CHOICES = [
        ('ตรวจสุขภาพ', 'ตรวจสุขภาพ'),
        ('ฉีดวัคซีน', 'ฉีดวัคซีน'),
        ('ผ่าตัด', 'ผ่าตัด'),
        ('อาบน้ำ-ตัดขน', 'อาบน้ำ-ตัดขน'),
        ('ทำหมัน', 'ทำหมัน'),
        ('ทำฟัน', 'ทำฟัน'),
        ('อื่นๆ', 'อื่นๆ'),
    ]
    ref_no = models.CharField(max_length=20, blank=True, null=True, verbose_name='เลขที่ใบนัด')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, verbose_name='สัตว์เลี้ยง')
    vet = models.ForeignKey(Vet, on_delete=models.CASCADE, verbose_name='สัตวแพทย์')
    appointment_date = models.DateField(blank=True, null=True, verbose_name='วันที่นัด')
    appointment_time = models.TimeField(blank=True, null=True, verbose_name='เวลานัด')
    service_type = models.CharField(max_length=50, choices=SERVICE_CHOICES, blank=True, null=True, verbose_name='ประเภทบริการ')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='สถานะ')
    reason = models.TextField(blank=True, null=True, verbose_name='อาการ/หมายเหตุ')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    def save(self, *args, **kwargs):
        if not self.ref_no:
            import random
            self.ref_no = f"APT{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)
    def __str__(self):
        pet_name = self.pet.name if self.pet else "?"
        return f"นัดหมาย {pet_name} วันที่ {self.appointment_date}"
class MedicalRecord(models.Model):
    VISIT_TYPE_CHOICES = [
        ('ตรวจสุขภาพทั่วไป', 'ตรวจสุขภาพทั่วไป'),
        ('ฉีดวัคซีน', 'ฉีดวัคซีน'),
        ('รักษาโรค', 'รักษาโรค'),
        ('ผ่าตัด', 'ผ่าตัด'),
        ('ทำหมัน', 'ทำหมัน'),
        ('อาบน้ำ-ตัดขน', 'อาบน้ำ-ตัดขน'),
        ('ฉุกเฉิน', 'ฉุกเฉิน'),
        ('อื่นๆ', 'อื่นๆ'),
    ]
    ref_no      = models.CharField(max_length=20, blank=True, null=True, verbose_name='เลขที่เอกสาร')
    pet         = models.ForeignKey(Pet, on_delete=models.CASCADE, verbose_name='สัตว์เลี้ยง')
    vet         = models.ForeignKey(Vet, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='สัตวแพทย์')
    visit_date  = models.DateField(blank=True, null=True, verbose_name='วันที่เข้ารับบริการ')
    visit_type  = models.CharField(max_length=50, choices=VISIT_TYPE_CHOICES, blank=True, null=True, verbose_name='ประเภทการเข้ารับบริการ')
    weight      = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='น้ำหนัก (กก.)')
    temperature = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True, verbose_name='อุณหภูมิ (°C)')
    symptoms    = models.TextField(blank=True, null=True, verbose_name='อาการที่พบ')
    diagnosis   = models.TextField(verbose_name='ผลการวินิจฉัย')
    treatment   = models.TextField(verbose_name='วิธีการรักษา')
    medicines   = models.ManyToManyField(Medicine, blank=True, verbose_name='ยาที่ใช้')
    cost        = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='ค่าใช้จ่าย')
    is_paid     = models.BooleanField(default=False, verbose_name='สถานะการชำระเงิน')
    next_visit  = models.DateField(blank=True, null=True, verbose_name='วันนัดครั้งต่อไป')
    notes       = models.TextField(blank=True, null=True, verbose_name='หมายเหตุเพิ่มเติม')
    created_at  = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        if not self.ref_no:
            import random
            self.ref_no = f"MR{random.randint(100000, 999999)}"
        super().save(*args, **kwargs)
    def __str__(self):
        pet_name = self.pet.name if self.pet else "?"
        return f"ประวัติการรักษา {pet_name} เมื่อ {self.visit_date or self.created_at}"
class AuditLog(models.Model):
    table_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='ชื่อตาราง')
    record_id = models.IntegerField(blank=True, null=True, verbose_name='ID ของบรรทัดที่แก้')
    action_type = models.CharField(max_length=50, blank=True, null=True, verbose_name='ประเภทคำสั่ง')
    old_value = models.TextField(blank=True, null=True, verbose_name='ค่าเดิม')
    new_value = models.TextField(blank=True, null=True, verbose_name='ค่าใหม่')
    changed_by = models.CharField(max_length=100, blank=True, null=True, verbose_name='ผู้แก้')
    change_date = models.DateTimeField(blank=True, null=True, verbose_name='ผู้แก้')
    class Meta:
        db_table = 'myapp_audit_logs'
        managed = False
class VetLicenseLog(models.Model):
    vet_id = models.IntegerField(blank=True, null=True, verbose_name='ID หมอ')
    old_license_no = models.CharField(max_length=50, blank=True, null=True)
    new_license_no = models.CharField(max_length=50, blank=True, null=True)
    change_date = models.DateTimeField(blank=True, null=True)
    class Meta:
        db_table = 'myapp_vet_license_log'
        managed = False