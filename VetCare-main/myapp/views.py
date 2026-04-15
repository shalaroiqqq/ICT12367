from django.db import models, connection
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import Http404
from .models import Owner, Pet, Vet, Medicine, Appointment, MedicalRecord
from .forms import (
    OwnerForm, VetForm, PetForm, AppointmentForm, MedicineForm, MedicalRecordForm,
    CustomUserCreationForm, CustomAuthenticationForm
)
from django.db.models import Count, Q, F
from django.db.models.functions import Cast, Concat
from django.db.models import CharField, Value
from django.db.models.expressions import RawSQL
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, date, timedelta
import re
from django.contrib.auth.mixins import UserPassesTestMixin
class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not self.test_func():
            messages.warning(request, "ขออภัย! คุณไม่มีสิทธิ์เข้าถึงส่วนนี้ (เฉพาะพนักงานเท่านั้น)")
            prev_url = request.META.get('HTTP_REFERER', 'client_dashboard')
            current_url = request.build_absolute_uri()
            if prev_url == current_url:
                prev_url = 'client_dashboard'
            return redirect(prev_url)
        return super().dispatch(request, *args, **kwargs)
from functools import wraps
def staff_required_redirect(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_staff:
            messages.warning(request, "ขออภัย! คุณไม่มีสิทธิ์เข้าถึงหน้านี้ (เฉพาะพนักงาน)")
            return redirect('client_dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
MONTH_MAP = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
}
def date_search_q(q_str, field='birth_date'):
    q_lower = q_str.strip().lower()
    filters = {}
    year_match = re.search(r'\b(19|20)\d{2}\b', q_lower)
    if year_match:
        filters[f'{field}__year'] = int(year_match.group())
    for mname, mnum in MONTH_MAP.items():
        if mname in q_lower:
            filters[f'{field}__month'] = mnum
            break
    q_no_year = re.sub(r'\b(19|20)\d{2}\b', '', q_lower)
    day_match = re.search(r'\b(\d{1,2})\b', q_no_year)
    if day_match:
        filters[f'{field}__day'] = int(day_match.group(1))
    if filters:
        return models.Q(**filters)
    return None
@login_required
def dashboard(request):
    if not request.user.is_staff:
        messages.info(request, "ระบบได้โอนย้ายคุณไปยังหน้าหลักสำหรับลูกค้า")
        return redirect('client_dashboard')
    pet_species_data = list(Pet.objects.values('species').annotate(count=Count('id')))
    recent_records = MedicalRecord.objects.select_related('pet').order_by('-created_at')[:5]
    from datetime import date, timedelta
    threshold = date.today() + timedelta(days=30)
    expiring_medicines = Medicine.objects.filter(expiry_date__lt=threshold).values('name', 'expiry_date', 'stock')
    today = date.today()
    monthly_revenue_agg = MedicalRecord.objects.filter(
        visit_date__year=today.year,
        visit_date__month=today.month
    ).aggregate(total=models.Sum('cost'))
    monthly_revenue = monthly_revenue_agg['total'] or 0
    context = {
        'owners_count': Owner.objects.count(),
        'pets_count': Pet.objects.count(),
        'vets_count': Vet.objects.count(),
        'appointments_count': Appointment.objects.count(),
        'medical_records_count': MedicalRecord.objects.count(),
        'medicines_count': Medicine.objects.count(),
        'pet_species_data': pet_species_data,
        'recent_records': recent_records,
        'expiring_medicines': expiring_medicines,
        'monthly_revenue': monthly_revenue,
    }
    return render(request, 'myapp/core/dashboard.html', context)
@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.warning(request, "คุณไม่มีสิทธิ์เข้าถึงหน้าผู้ดูแลระบบ ระบบได้โอนย้ายคุณมายัง Client Portal")
        return redirect('client_dashboard')
    pet_species_data = list(Pet.objects.values('species').annotate(count=Count('id')))
    recent_records = MedicalRecord.objects.select_related('pet').order_by('-created_at')[:5]
    from datetime import date, timedelta
    threshold = date.today() + timedelta(days=30)
    expiring_medicines = Medicine.objects.filter(expiry_date__lt=threshold).values('name', 'expiry_date', 'stock')
    today = date.today()
    monthly_revenue_agg = MedicalRecord.objects.filter(
        visit_date__year=today.year,
        visit_date__month=today.month
    ).aggregate(total=models.Sum('cost'))
    monthly_revenue = monthly_revenue_agg['total'] or 0
    context = {
        'owners_count': Owner.objects.count(),
        'pets_count': Pet.objects.count(),
        'vets_count': Vet.objects.count(),
        'appointments_count': Appointment.objects.count(),
        'medical_records_count': MedicalRecord.objects.count(),
        'medicines_count': Medicine.objects.count(),
        'recent_appointments': Appointment.objects.all().order_by('-appointment_date', '-appointment_time')[:5],
        'recent_records': recent_records,
        'pet_species_data': pet_species_data,
        'expiring_medicines': expiring_medicines,
        'monthly_revenue': monthly_revenue,
    }
    return render(request, 'myapp/admin/admin_dashboard.html', context)
def admin_owners(request):
    q = request.GET.get('q', '')
    owners = Owner.objects.all().annotate(
        full_name=Concat('first_name', Value(' '), 'last_name')
    )
    if q:
        owners = owners.filter(
            models.Q(customer_id__icontains=q) |
            models.Q(first_name__icontains=q) |
            models.Q(last_name__icontains=q) |
            models.Q(full_name__icontains=q) |
            models.Q(phone__icontains=q)
        )
    return render(request, 'myapp/admin/admin_owners.html', {'owners': owners, 'q': q})
def admin_owner_delete(request, pk):
    owner = get_object_or_404(Owner, pk=pk)
    if request.method == 'POST':
        owner.delete()
        messages.success(request, f'ลบเจ้าของสัตว์ {owner.first_name} {owner.last_name} สำเร็จ')
        return redirect('admin_owners')
    return render(request, 'myapp/core/confirm_delete.html', {
        'item_name': f'{owner.first_name} {owner.last_name}',
        'back_url': '/admin/owners/',
        'extra_info': 'การกระทำนี้จะลบสัตว์เลี้ยงทั้งหมดของเจ้าของนี้ด้วย'
    })
def admin_pets(request):
    q = request.GET.get('q', '')
    pets = Pet.objects.all().select_related('owner').annotate(
        owner_full_name=Concat('owner__first_name', Value(' '), 'owner__last_name')
    )
    if q:
        filter_q = models.Q(name__icontains=q) | \
                   models.Q(species__icontains=q) | \
                   models.Q(customer_id__icontains=q) | \
                   models.Q(owner__first_name__icontains=q) | \
                   models.Q(owner__last_name__icontains=q) | \
                   models.Q(owner_full_name__icontains=q) | \
                   models.Q(owner__phone__icontains=q) | \
                   models.Q(owner__customer_id__icontains=q)
        date_query = date_search_q(q, field='birth_date')
        if date_query:
            filter_q |= date_query
        pets = pets.filter(filter_q)
    pets = pets.annotate(
        age_from_sql=RawSQL("(strftime('%Y', 'now') - strftime('%Y', birth_date)) || ' ปี ' || ((strftime('%m', 'now') - strftime('%m', birth_date) + 12) % 12) || ' เดือน'", []),
        visit_count_sql=RawSQL("(SELECT COUNT(*) FROM myapp_medicalrecord mr WHERE mr.pet_id = myapp_pet.id)", []),
        total_spending_sql=RawSQL("(SELECT COALESCE(SUM(cost), 0) FROM myapp_medicalrecord mr WHERE mr.pet_id = myapp_pet.id)", [])
    )
    return render(request, 'myapp/admin/admin_pets.html', {'pets': pets, 'q': q})
def sql_clinic_dashboard(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM v_ClinicDashboard")
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        try:
            cursor.execute("SELECT * FROM v_TodaysAppointments")
            apt_columns = [col[0] for col in cursor.description]
            apt_rows = [dict(zip(apt_columns, row)) for row in cursor.fetchall()]
        except Exception:
            apt_rows = []
        try:
            cursor.execute("SELECT * FROM v_VetWorkload")
            vet_columns = [col[0] for col in cursor.description]
            vet_rows = [dict(zip(vet_columns, row)) for row in cursor.fetchall()]
        except Exception:
            vet_rows = []
        try:
            cursor.execute("SELECT SUM(cost) FROM myapp_medicalrecord")
            revenue_result = cursor.fetchone()[0]
            clinic_total_revenue = "{:,.2f}".format(float(revenue_result)) if revenue_result else "0.00"
        except Exception:
            clinic_total_revenue = "0.00"
        try:
            cursor.execute("SELECT SUM(stock * selling_price) FROM myapp_medicine")
            stock_result = cursor.fetchone()[0]
            clinic_total_stock_value = "{:,.2f}".format(float(stock_result)) if stock_result else "0.00"
        except Exception:
            clinic_total_stock_value = "0.00"
    from django.conf import settings
    engine = settings.DATABASES['default']['ENGINE']
    if 'mssql' in engine:
        db_type = 'SQL Server'
        db_icon = 'fas fa-database'
        db_color = 'text-primary'
    else:
        db_type = 'SQLite'
        db_icon = 'fas fa-file-database'
        db_color = 'text-success'
    from django.db.models.expressions import RawSQL
    pets = Pet.objects.all().annotate(
        total_spending=RawSQL("(SELECT COALESCE(SUM(cost), 0) FROM myapp_medicalrecord mr WHERE mr.pet_id = myapp_pet.id)", []),
        pet_age=RawSQL("(strftime('%Y', 'now') - strftime('%Y', birth_date)) || ' ปี '", []),
        visit_count=RawSQL("(SELECT COUNT(*) FROM myapp_medicalrecord mr WHERE mr.pet_id = myapp_pet.id)", [])
    )
    medicines = Medicine.objects.all().annotate(
        is_low_stock_sql=RawSQL("CASE WHEN stock <= reorder_point THEN 1 ELSE 0 END", [])
    )
    context = {
        'clinic_data': rows,
        'todays_appointments': apt_rows,
        'vet_workload': vet_rows,
        'clinic_total_revenue': clinic_total_revenue,
        'clinic_total_stock_value': clinic_total_stock_value,

        'pets': pets,
        'vets': Vet.objects.all(),
        'medicines': medicines,
        'owners': Owner.objects.all(),
        'db_type': db_type,
        'db_icon': db_icon,
        'db_color': db_color,
    }
    return render(request, 'myapp/admin/sql_dashboard.html', context)
@login_required
def quick_record_treatment(request):
    if request.method == 'POST':
        pet_name = request.POST.get('pet_name')
        vet_first_name = request.POST.get('vet_first_name')
        medicine_id = request.POST.get('medicine_id')
        total_cost = request.POST.get('total_cost')
        try:
            from django.db import transaction
            with transaction.atomic():
                pet = Pet.objects.get(name=pet_name)
                vet = Vet.objects.get(first_name=vet_first_name)
                record = MedicalRecord.objects.create(
                    pet=pet,
                    vet=vet,
                    cost=total_cost,
                    visit_date=timezone.now().date(),
                    diagnosis='Checkup',
                    treatment='Treated',
                    is_paid=True
                )
                if medicine_id:
                    record.medicines.add(medicine_id)
            messages.success(request, f"สำเร็จ: บันทึกข้อมูลการรักษาด่วน (SQLite Transaction) ของ {pet_name} เรียบร้อยแล้ว")
        except Exception as e:
            messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")
    return redirect('sql_clinic_dashboard')
@login_required
def cleanup_old_logs(request):
    if not request.user.is_staff:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
             return JsonResponse({'success': False, 'error': "Access Denied: You must be a Staff member."})
        messages.error(request, "Access Denied: Only staff can perform DB Maintenance.")
        return redirect('sql_clinic_dashboard')
    if request.method == 'POST':
        days = request.POST.get('days_old', 30)
        try:
            days_int = int(days)
            from django.utils import timezone
            from datetime import timedelta
            cutoff = timezone.now() - timedelta(days=days_int)
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM myapp_audit_logs WHERE change_date < %s", [cutoff])
            msg = f"สำเร็จ: เคลียร์ Log ของระบบที่เก่ากว่า {days_int} วัน เรียบร้อยแล้ว (ระบบได้รับการเพิ่มประสิทธิภาพ)"
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': msg})
            messages.success(request, msg)
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            messages.error(request, f"Error during cleanup: {str(e)}")
    return redirect('sql_clinic_dashboard')
@login_required
def quick_register_patient(request):
    if request.method == 'POST':
        owner_first = request.POST.get('owner_first_name')
        owner_last = request.POST.get('owner_last_name')
        owner_phone = request.POST.get('owner_phone')
        pet_name = request.POST.get('pet_name')
        pet_species = request.POST.get('pet_species')
        pet_breed = request.POST.get('pet_breed', '') # Optional breed
        try:
            from django.db import transaction
            with transaction.atomic():
                owner = Owner.objects.create(
                    first_name=owner_first,
                    last_name=owner_last,
                    phone=owner_phone
                )
                Pet.objects.create(
                    owner=owner,
                    name=pet_name,
                    species=pet_species,
                    breed=pet_breed
                )
            messages.success(request, f"สำเร็จ: สร้างประวัติเจ้าของใหม่ ({owner_first}) และเชื่อมโยงสัตว์เลี้ยง ({pet_name}) เรียบร้อยแล้ว")
        except Exception as e:
            messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")
    return redirect('sql_clinic_dashboard')
@login_required
def sql_update_phone(request):
    if request.method == 'POST':
        owner_name = request.POST.get('owner_name')
        new_phone = request.POST.get('new_phone')
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE v_ClinicDashboard SET OwnerPhone = %s WHERE OwnerName = %s",
                    [new_phone, owner_name]
                )
            messages.success(request, f"สำเร็จ: อัปเดตเบอร์โทรของ '{owner_name}' เป็น '{new_phone}' ผ่าน View เรียบร้อยแล้ว (SQLite Trigger ทำงาน)")
        except Exception as e:
            messages.error(request, f"เกิดข้อผิดพลาดในการอัปเดตข้อมูล: {str(e)}")
    return redirect('sql_clinic_dashboard')
@login_required
def sql_update_stock(request):
    if request.method == 'POST':
        medicine_id = request.POST.get('medicine_id')
        new_stock = request.POST.get('new_stock')
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE v_MedicineStockReport SET stock = %s WHERE id = %s",
                    [new_stock, medicine_id]
                )
            from django.http import JsonResponse
            return JsonResponse({'success': True, 'message': f'อัปเดตสต็อกยา (รหัส {medicine_id}) เป็น {new_stock} ชิ้น เรียบร้อยแล้ว'})
        except Exception as e:
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    from django.http import JsonResponse
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
@login_required
def sql_update_pet_info(request):
    if request.method == 'POST':
        pet_id = request.POST.get('pet_id')
        new_pet_name = request.POST.get('new_pet_name', '').strip()
        new_species = request.POST.get('new_species', '').strip()
        new_phone = request.POST.get('new_phone', '').strip()
        try:
            with connection.cursor() as cursor:
                update_fields = []
                params = []
                if new_pet_name:
                    update_fields.append("pet_name = %s")
                    params.append(new_pet_name)
                if new_species:
                    update_fields.append("species = %s")
                    params.append(new_species)
                if new_phone:
                    update_fields.append("owner_phone = %s")
                    params.append(new_phone)
                if update_fields:
                    params.append(pet_id)
                    query = f"UPDATE v_OwnerPetSummary SET {', '.join(update_fields).replace('%s', '?')} WHERE pet_id = ?"
                    cursor.execute(query, params)
                    messages.success(request, f"สำเร็จ: อัปเดตข้อมูลผ่าน View เรียบร้อยแล้ว (SQLite Trigger)")
                else:
                    messages.warning(request, "ไม่ได้รับข้อมูลใหม่สำหรับการอัปเดต")
        except Exception as e:
            messages.error(request, f"เกิดข้อผิดพลาดในการอัปเดตข้อมูล: {str(e)}")
    return redirect('sql_clinic_dashboard')
@login_required
def sql_update_appointment_status(request):
    if request.method == 'POST':
        apt_id = request.POST.get('appointment_id')
        new_status = request.POST.get('new_status')
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE v_TodaysAppointments SET status = %s WHERE appointment_id = %s",
                    [new_status, apt_id]
                )
            messages.success(request, f"สำเร็จ: อัปเดตสถานะนัดหมาย (รหัส {apt_id}) เป็น '{new_status}' ผ่าน View เรียบร้อยแล้ว (SQLite)")
        except Exception as e:
            messages.error(request, f"เกิดข้อผิดพลาดในการอัปเดตสถานะนัดหมาย: {str(e)}")
    return redirect('sql_clinic_dashboard')
@login_required
def sql_update_vet_workload(request):
    if request.method == 'POST':
        vet_id = request.POST.get('vet_id')
        new_hours = request.POST.get('new_hours')
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE v_VetWorkload SET working_hours = %s WHERE vet_id = %s",
                    [new_hours, vet_id]
                )
            messages.success(request, f"สำเร็จ: อัปเดตชั่วโมงทำงานของแพทย์ (รหัส {vet_id}) เป็น {new_hours} ผ่าน View เรียบร้อยแล้ว (SQLite)")
        except Exception as e:
            messages.error(request, f"เกิดข้อผิดพลาดในการอัปเดตชั่วโมงทำงาน: {str(e)}")
    return redirect('sql_clinic_dashboard')
@login_required
def sql_sp_apply_member_discount(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id', '').strip()
        discount_percent = request.POST.get('discount_percent', 10)
        try:
            discount_val = float(discount_percent) / 100.0
            owner = get_object_or_404(Owner, customer_id=customer_id)
            records = MedicalRecord.objects.filter(pet__owner=owner)
            if not records.exists():
                messages.warning(request, f"ไม่พบประวัติการรักษาสำหรับสมาชิก {customer_id}")
                return redirect('sql_clinic_dashboard')
            count = 0
            for rec in records:
                if rec.pet.price_level == 'ราคาพิเศษ':
                    multiplier = 1.0 - discount_val
                    rec.cost = float(rec.cost) * multiplier
                    rec.save(update_fields=['cost'])
                    count += 1
            messages.success(request, f"สำเร็จ: ปรับปรุงส่วนลด {discount_percent}% ให้สมาชิก '{owner.first_name}' ทั้งหมด {count} รายการเรียบร้อยแล้ว")
        except Exception as e:
            messages.error(request, f"เกิดข้อผิดพลาดในการประมวลผล: {str(e)}")
    return redirect('sql_clinic_dashboard')
@login_required
def sql_sp_batch_update_price(request):
    if request.method == 'POST':
        percentage = request.POST.get('percentage')
        try:
            percent_val = Decimal(percentage) / 100
            Medicine.objects.all().update(selling_price=F('selling_price') * (1 + percent_val))
            messages.success(request, f"สำเร็จ: อัปเดตราคาแบบกลุ่ม (Batch Update) ด้วย Percentage {percentage}% เรียบร้อยแล้ว (SQLite ORM)")
        except Exception as e:
            messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")
    return redirect('sql_clinic_dashboard')
@login_required
def sql_sp_check_expired_medicine(request):
    if request.method == 'POST':
        threshold_date = request.POST.get('threshold_date')
        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC [dbo].[sp_CheckExpiredMedicine] @ThresholdDate=%s", [threshold_date])
            messages.success(request, f"สำเร็จ: เรียกใช้งาน Stored Procedure เช็คยาหมดอายุ (อิงวันที่ {threshold_date}) เรียบร้อยแล้ว")
        except Exception as e:
            messages.error(request, f"เกิดข้อผิดพลาดในการเรียกใช้ Stored Procedure: {str(e)}")
    return redirect('sql_clinic_dashboard')
@login_required
def sql_sp_get_monthly_revenue(request):
    if request.method == 'POST':
        year = request.POST.get('year')
        month = request.POST.get('month')
        try:
            total = MedicalRecord.objects.filter(visit_date__year=year, visit_date__month=month).aggregate(total=models.Sum('cost'))['total'] or 0
            messages.success(request, f"สำเร็จ: รายรับรวมเดือน {month}/{year} คือ ฿{total} (คำนวณผ่าน SQLite ORM)")
        except Exception as e:
            messages.error(request, f"เกิดข้อผิดพลาด: {str(e)}")
    return redirect('sql_clinic_dashboard')
def admin_pet_delete(request, pk):
    pet = get_object_or_404(Pet, pk=pk)
    if request.method == 'POST':
        pet_name = pet.name
        pet.delete()
        messages.success(request, f'ลบสัตว์เลี้ยง {pet_name} สำเร็จ')
        return redirect('admin_pets')
    return render(request, 'myapp/core/confirm_delete.html', {
        'item_name': pet.name,
        'back_url': '/admin/pets/',
        'extra_info': 'การกระทำนี้จะลบปรวัติการรักษาทั้งหมดด้วย'
    })
def admin_appointments(request):
    q = request.GET.get('q', '')
    appointments = Appointment.objects.all().select_related('pet', 'vet').order_by('-appointment_date', '-appointment_time').annotate(
        pet_summary_name=Concat('pet__name', Value(' ('), 'pet__species', Value(')'))
    )
    if q:
        appointments = appointments.filter(
            models.Q(pet__name__icontains=q) |
            models.Q(vet__first_name__icontains=q) |
            models.Q(service_type__icontains=q)
        )
    return render(request, 'myapp/admin/admin_appointments.html', {'appointments': appointments, 'q': q})
def admin_appointment_delete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, 'ลบการนัดหมายสำเร็จ')
        return redirect('admin_appointments')
    return render(request, 'myapp/core/confirm_delete.html', {
        'item_name': f'การนัดหมาย - {appointment.pet.name}',
        'back_url': '/admin/appointments/',
        'extra_info': f'วันที่: {appointment.appointment_date.strftime("%d/%m/%Y")} {appointment.appointment_time.strftime("%H:%M")}'
    })
def admin_medical_records(request):
    q = request.GET.get('q', '')
    records = MedicalRecord.objects.all().select_related('pet', 'vet').order_by('-created_at').annotate(
        pet_summary_name=Concat('pet__name', Value(' ('), 'pet__species', Value(')'))
    )
    if q:
        records = records.filter(
            models.Q(pet__name__icontains=q) |
            models.Q(diagnosis__icontains=q) |
            models.Q(ref_no__icontains=q)
        )
    return render(request, 'myapp/admin/admin_medical_records.html', {'records': records, 'q': q})
def admin_medical_record_delete(request, pk):
    record = get_object_or_404(MedicalRecord, pk=pk)
    if request.method == 'POST':
        record.delete()
        messages.success(request, 'ลบประวัติการรักษาสำเร็จ')
        return redirect('admin_medical_records')
    return render(request, 'myapp/core/confirm_delete.html', {
        'item_name': f'ประวัติการรักษา - {record.pet.name}',
        'back_url': '/admin/medical-records/',
        'extra_info': f'วันที่: {record.created_at.strftime("%d/%m/%Y %H:%M")}'
    })
def admin_vets(request):
    vets = Vet.objects.all()
    return render(request, 'myapp/admin/admin_vets.html', {'vets': vets})
def admin_medicines(request):
    medicines = Medicine.objects.all().annotate(
        stock_value_sql=ExpressionWrapper(F('stock') * F('selling_price'), output_field=DecimalField()),
        is_low_stock_sql=ExpressionWrapper(Q(stock__lte=F('reorder_point')), output_field=BooleanField())
    )
    return render(request, 'myapp/admin/admin_medicines.html', {'medicines': medicines})
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
@login_required
def admin_user_management(request):
    if not request.user.is_superuser:
        messages.error(request, 'คุณไม่มีสิทธิ์เข้าถึงส่วนนี้ (เฉพาะ Admin สูงสุดเท่านั้น)')
        return redirect('admin_dashboard')
    q = request.GET.get('q', '').strip()
    users = User.objects.all().order_by('-date_joined')
    if q:
        for term in q.split():
            users = users.filter(
                Q(username__icontains=term) |
                Q(email__icontains=term) |
                Q(first_name__icontains=term) |
                Q(last_name__icontains=term)
            )
    return render(request, 'myapp/admin/admin_user_management.html', {'users': users, 'q': q})
@login_required
def admin_user_toggle_status(request, user_id, field):
    if not request.user.is_superuser:
        messages.error(request, 'คุณไม่มีสิทธิ์แก้ไขข้อมูลผู้ใช้')
        return redirect('admin_user_management')
    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user and field in ['is_staff', 'is_superuser']:
        messages.warning(request, 'คุณไม่สามารถเปลี่ยนสถานะของตัวเองเพื่อความปลอดภัย')
        return redirect('admin_user_management')
    if field == 'staff':
        target_user.is_staff = not target_user.is_staff
        status = 'พนักงาน (Staff)' if target_user.is_staff else 'ผู้ใช้ทั่วไป'
    elif field == 'admin':
        target_user.is_superuser = not target_user.is_superuser
        if target_user.is_superuser:
            target_user.is_staff = True
        status = 'Admin สูงสุด' if target_user.is_superuser else 'ผู้ใช้งานปกติ'
    target_user.save()
    messages.success(request, f'อัปเดตสถานะของ {target_user.username} เป็น {status} เรียบร้อยแล้ว')
    return redirect('admin_user_management')
@login_required
def admin_user_edit(request, user_id):
    if not request.user.is_superuser:
        messages.error(request, 'คุณไม่มีสิทธิ์แก้ไขข้อมูลผู้ใช้')
        return redirect('admin_dashboard')
    target_user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        target_user.username = request.POST.get('username')
        target_user.email = request.POST.get('email')
        target_user.first_name = request.POST.get('first_name')
        target_user.last_name = request.POST.get('last_name')
        new_password = request.POST.get('new_password', '').strip()
        if new_password:
            target_user.set_password(new_password)
        if target_user != request.user:
            target_user.is_staff = 'is_staff' in request.POST
            target_user.is_superuser = 'is_superuser' in request.POST
            if target_user.is_superuser:
                target_user.is_staff = True
        try:
            target_user.save()
            messages.success(request, f'อัปเดตข้อมูลของ {target_user.username} สำเร็จ')
            return redirect('admin_user_management')
        except Exception as e:
            messages.error(request, f'เกิดข้อผิดพลาด: {str(e)}')
    return render(request, 'myapp/admin/admin_user_edit.html', {'target_user': target_user})
@login_required
def admin_user_delete(request, user_id):
    if not request.user.is_superuser:
        messages.error(request, 'คุณไม่มีสิทธิ์ลบผู้ใช้')
        return redirect('admin_user_management')
    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        messages.error(request, 'คุณไม่สามารถลบบัญชีของตัวเองได้!')
        return redirect('admin_user_management')
    if request.method == 'POST':
        username = target_user.username
        target_user.delete()
        messages.success(request, f'ลบบัญชี {username} เรียบร้อยแล้ว')
        return redirect('admin_user_management')
    return render(request, 'myapp/core/confirm_delete.html', {
        'item_name': f'บัญชีผู้ใช้: {target_user.username} ({target_user.email})',
        'back_url': '/admin-backend/users/',
        'extra_info': 'คำเตือน: การลบบัญชีผู้ใช้จะส่งผลต่อข้อมูลที่เกี่ยวข้องกับผู้ใช้นี้ทั้งหมด'
    })
from django.conf import settings
def register(request):
    if request.user.is_authenticated:
        return redirect('owner_profile')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'ลงทะเบียนสำเร็จ! กรุณาเข้าสู่ระบบ')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'myapp/auth/register.html', {'form': form})
class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'myapp/auth/login.html'
    redirect_authenticated_user = True
    def get_success_url(self):
        user = self.request.user
        if user.is_staff:
            return reverse_lazy('admin_dashboard')
        return reverse_lazy('client_dashboard')
def custom_logout(request):
    logout(request)
    return redirect('login')
def owner_profile(request):
    if not request.user.is_authenticated:
        owner = Owner.objects.first()
    else:
        owner = getattr(request.user, 'owner_profile', None)
    if not owner:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('client_register_pet')
    pets = owner.pets.all()
    medical_records = MedicalRecord.objects.filter(pet__owner=owner).order_by('-created_at')[:5]
    context = {
        'owner': owner,
        'pets': pets,
        'medical_records': medical_records,
    }
    return render(request, 'myapp/owner/owner_profile.html', context)
def owner_pets(request):
    owner = getattr(request.user, 'owner_profile', None)
    if not owner:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        messages.warning(request, 'ไม่พบข้อมูลเจ้าของสัตว์')
        return redirect('owner_profile')
    pets = owner.pets.all()
    context = {
        'owner': owner,
        'pets': pets,
    }
    return render(request, 'myapp/owner/owner_pets.html', context)

@login_required
def client_pet_delete(request, pk):
    owner = getattr(request.user, 'owner_profile', None)
    if not owner:
        return redirect('client_profile')
    pet = get_object_or_404(Pet, pk=pk, owner=owner)
    pet_name = pet.name
    
    # Optional: Delete image from storage
    if pet.image:
        pet.image.delete(save=False)
        
    pet.delete()
    messages.success(request, f'ลบข้อมูล {pet_name} ออกจากระบบเรียบร้อยแล้ว')
    return redirect('client_dashboard')
def owner_appointments(request):
    owner = getattr(request.user, 'owner_profile', None)
    if not owner:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        messages.warning(request, 'ไม่พบข้อมูลเจ้าของสัตว์')
        return redirect('owner_profile')
    appointments = Appointment.objects.filter(pet__owner=owner).order_by('-created_at')
    context = {
        'owner': owner,
        'appointments': appointments,
    }
    return render(request, 'myapp/owner/owner_appointments.html', context)
class OwnerListView(ListView):
    model = Owner
    template_name = 'myapp/owner/owner_list.html'
    context_object_name = 'owners'
    paginate_by = 10
    def get_queryset(self):
        qs = super().get_queryset().annotate(
            full_name=Concat('first_name', Value(' '), 'last_name')
        )
        q = self.request.GET.get('q', '')
        if q:
            qs = qs.filter(
                models.Q(customer_id__icontains=q) |
                models.Q(first_name__icontains=q) |
                models.Q(last_name__icontains=q) |
                models.Q(full_name__icontains=q) |
                models.Q(phone__icontains=q) |
                models.Q(address__icontains=q)
            )
        return qs.order_by('first_name')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        return context
class OwnerDetailView(DetailView):
    model = Owner
    template_name = 'myapp/owner/owner_detail.html'
    context_object_name = 'owner'
class OwnerCreateView(CreateView):
    model = Owner
    template_name = 'myapp/owner/owner_form.html'
    form_class = OwnerForm
    success_url = reverse_lazy('owner_list')
class OwnerUpdateView(UpdateView):
    model = Owner
    template_name = 'myapp/owner/owner_form.html'
    form_class = OwnerForm
    success_url = reverse_lazy('owner_list')
    def get_initial(self):
        initial = super().get_initial()
        owner = self.get_object()
        if owner.address and " | " in owner.address:
            parts = owner.address.split(" | ", 1)
            initial['address_1'] = parts[0]
            initial['address_2'] = parts[1]
        else:
            initial['address_1'] = owner.address
        return initial
    def form_valid(self, form):
        owner = form.save(commit=False)
        addr1 = form.cleaned_data.get('address_1', '').strip()
        addr2 = form.cleaned_data.get('address_2', '').strip()
        owner.address = f"{addr1} | {addr2}".strip() if addr1 or addr2 else ""
        owner.save()
        messages.success(self.request, "แก้ไขข้อมูลเจ้าของสัตว์เรียบร้อยแล้ว")
        return super().form_valid(form)
class OwnerDeleteView(DeleteView):
    model = Owner
    template_name = 'myapp/core/confirm_delete.html'
    success_url = reverse_lazy('owner_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        owner = self.get_object()
        context['item_name'] = f'{owner.first_name} {owner.last_name}'
        context['back_url'] = reverse_lazy('owner_list')
        context['extra_info'] = 'การกระทำนี้ไม่สามารถยกเลิกได้'
        return context
class PetListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Pet
    template_name = 'myapp/pet/pet_list.html'
    context_object_name = 'pets'
    paginate_by = 10
    login_url = 'login'
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff
    def get_queryset(self):
        qs = super().get_queryset().select_related('owner').annotate(
            owner_full_name=Concat('owner__first_name', Value(' '), 'owner__last_name')
        )
        q = self.request.GET.get('q', '')
        if q:
            filter_q = models.Q(name__icontains=q) | \
                       models.Q(species__icontains=q) | \
                       models.Q(breed__icontains=q) | \
                       models.Q(customer_id__icontains=q) | \
                       models.Q(owner__first_name__icontains=q) | \
                       models.Q(owner__last_name__icontains=q) | \
                       models.Q(owner_full_name__icontains=q) | \
                       models.Q(owner__phone__icontains=q) | \
                       models.Q(owner__customer_id__icontains=q)
            date_query = date_search_q(q, field='birth_date')
            if date_query:
                filter_q |= date_query
            qs = qs.filter(filter_q)
        return qs.order_by('name')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        return context
class PetDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Pet
    template_name = 'myapp/pet/pet_detail.html'
    context_object_name = 'pet'
    login_url = 'login'
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff
class PetCreateView(CreateView):
    model = Pet
    template_name = 'myapp/pet/pet_form.html'
    form_class = PetForm
    success_url = reverse_lazy('pet_list')
    def form_valid(self, form):
        first_name = form.cleaned_data.get('owner_first_name')
        last_name = form.cleaned_data.get('owner_last_name')
        phone = form.cleaned_data.get('owner_phone')
        address_1 = form.cleaned_data.get('owner_address_1', '')
        address_2 = form.cleaned_data.get('owner_address_2', '')
        full_address = f"{address_1} {address_2}".strip()
        owner, created = Owner.objects.get_or_create(
            first_name=first_name,
            last_name=last_name,
            defaults={'phone': phone, 'address': full_address}
        )
        if not created:
            owner.phone = phone
            owner.address = full_address
            owner.save()
        form.instance.owner = owner
        return super().form_valid(form)
class PetUpdateView(UpdateView):
    model = Pet
    template_name = 'myapp/pet/pet_form.html'
    form_class = PetForm
    success_url = reverse_lazy('pet_list')
    def get_initial(self):
        initial = super().get_initial()
        pet = self.get_object()
        if pet.owner:
            initial['owner_first_name'] = pet.owner.first_name
            initial['owner_last_name'] = pet.owner.last_name
            initial['owner_phone'] = pet.owner.phone
            initial['owner_address_1'] = pet.owner.address
        return initial
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pet = self.get_object()
        owner_has_account = False
        if pet.owner:
            linked_user = User.objects.filter(owner_profile=pet.owner).first()
            if linked_user and linked_user.email:
                owner_has_account = True
        context['owner_has_account'] = owner_has_account
        return context
    def form_valid(self, form):
        first_name = form.cleaned_data.get('owner_first_name')
        last_name = form.cleaned_data.get('owner_last_name')
        phone = form.cleaned_data.get('owner_phone')
        address_1 = form.cleaned_data.get('owner_address_1', '')
        address_2 = form.cleaned_data.get('owner_address_2', '')
        full_address = f"{address_1} {address_2}".strip()
        
        # Handle custom image clear checkbox
        if self.request.POST.get('image-clear'):
            form.instance.image = None

        owner, created = Owner.objects.get_or_create(
            first_name=first_name,
            last_name=last_name,
            defaults={'phone': phone, 'address': full_address}
        )
        if not created:
            owner.phone = phone
            owner.address = full_address
            owner.save()
        form.instance.owner = owner
        return super().form_valid(form)
class PetDeleteView(DeleteView):
    model = Pet
    template_name = 'myapp/core/confirm_delete.html'
    success_url = reverse_lazy('pet_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pet = self.get_object()
        context['item_name'] = pet.name
        context['back_url'] = reverse_lazy('pet_list')
        context['extra_info'] = 'การกระทำนี้ไม่สามารถยกเลิกได้'
        return context
class VetListView(StaffRequiredMixin, ListView):
    model = Vet
    template_name = 'myapp/vet/vet_list.html'
    context_object_name = 'vets'
    paginate_by = 10
    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '')
        if q:
            qs = qs.filter(
                models.Q(first_name__icontains=q) |
                models.Q(last_name__icontains=q) |
                models.Q(specialty__icontains=q)
            )
        return qs.order_by('first_name')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        return context
class VetDetailView(StaffRequiredMixin, DetailView):
    model = Vet
    template_name = 'myapp/vet/vet_detail.html'
    context_object_name = 'vet'
class VetCreateView(StaffRequiredMixin, CreateView):
    model = Vet
    template_name = 'myapp/vet/vet_form.html'
    form_class = VetForm
    success_url = reverse_lazy('vet_list')
class VetUpdateView(StaffRequiredMixin, UpdateView):
    model = Vet
    template_name = 'myapp/vet/vet_form.html'
    form_class = VetForm
    success_url = reverse_lazy('vet_list')
    def form_valid(self, form):
        # Handle custom image clear checkbox
        if self.request.POST.get('image-clear'):
            form.instance.image = None
        
        # We don't need manual filter().update() anymore, form.save() is better and handles ImageField
        response = super().form_valid(form)
        
        # Sync Vet model from other fields in cleaned_data just in case if needed, 
        # but ModelForm.save() handles all 'image' and meta-fields usually.
        return response
class VetDeleteView(StaffRequiredMixin, DeleteView):
    model = Vet
    template_name = 'myapp/core/confirm_delete.html'
    success_url = reverse_lazy('vet_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vet = self.get_object()
        context['item_name'] = f"{vet.first_name} {vet.last_name}"
        context['back_url'] = reverse_lazy('vet_list')
        context['extra_info'] = 'การกระทำนี้ไม่สามารถยกเลิกได้'
        return context
class MedicineListView(StaffRequiredMixin, ListView):
    model = Medicine
    template_name = 'myapp/medicine/medicine_list.html'
    context_object_name = 'medicines'
    paginate_by = 30
    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '').strip()
        category = self.request.GET.get('category', '').strip()
        sort_by = self.request.GET.get('sort', 'name').strip()
        low_stock = self.request.GET.get('low_stock', '')
        if q:
            qs = qs.filter(
                Q(name__icontains=q) |
                Q(product_id__icontains=q) |
                Q(barcode__icontains=q) |
                Q(generic_name__icontains=q)
            ).distinct()
        if category:
            qs = qs.filter(product_type=category)
        if low_stock == '1':
            qs = qs.filter(stock__lte=F('reorder_point'))
        if sort_by == 'name_desc':
            qs = qs.order_by('-name')
        elif sort_by == 'price_asc':
            qs = qs.order_by('selling_price')
        elif sort_by == 'price_desc':
            qs = qs.order_by('-selling_price')
        elif sort_by == 'stock_asc':
            qs = qs.order_by('stock')
        elif sort_by == 'stock_desc':
            qs = qs.order_by('-stock')
        else:
            qs = qs.order_by('name')
        return qs
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['category'] = self.request.GET.get('category', '')
        context['sort'] = self.request.GET.get('sort', 'name')
        context['low_stock'] = self.request.GET.get('low_stock', '')
        context['mode'] = self.request.GET.get('mode', 'list')
        context['low_stock_count'] = Medicine.objects.filter(stock__lte=F('reorder_point')).count()
        return context
class MedicineDetailView(StaffRequiredMixin, DetailView):
    model = Medicine
    template_name = 'myapp/medicine/medicine_detail.html'
    context_object_name = 'medicine'
class MedicineCreateView(StaffRequiredMixin, CreateView):
    model = Medicine
    template_name = 'myapp/medicine/medicine_form.html'
    form_class = MedicineForm
    success_url = reverse_lazy('medicine_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_medicines'] = Medicine.objects.order_by('-id')[:5]
        return context
class MedicineUpdateView(StaffRequiredMixin, UpdateView):
    model = Medicine
    template_name = 'myapp/medicine/medicine_form.html'
    form_class = MedicineForm
    success_url = reverse_lazy('medicine_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_medicines'] = Medicine.objects.order_by('-id')[:5]
        return context
    def form_valid(self, form):
        if self.request.POST.get('image-clear'):
            form.instance.image = None
        return super().form_valid(form)
class MedicineDeleteView(StaffRequiredMixin, DeleteView):
    model = Medicine
    template_name = 'myapp/core/confirm_delete.html'
    success_url = reverse_lazy('medicine_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        med = self.get_object()
        context['item_name'] = f"{med.name}"
        context['back_url'] = reverse_lazy('medicine_list')
        context['extra_info'] = 'การกระทำนี้ไม่สามารถยกเลิกได้'
        return context
@login_required
def batch_update_medicine_price(request):
    if not request.user.is_staff:
        messages.error(request, "คุณไม่มีสิทธิ์ใช้งานส่วนนี้")
        return redirect('medicine_list')
    if request.method == 'POST':
        percentage = request.POST.get('percentage')
        if percentage:
            try:
                p_val = float(percentage)
                multiplier = 1 + (p_val / 100)
                updated = Medicine.objects.all().update(selling_price=F('selling_price') * multiplier)
                messages.success(request, f"สำเร็จ! ระบบได้ปรับราคาสินค้า {updated} รายการ เรียบร้อยแล้ว (เพิ่ม/ลด {percentage}%)")
            except ValueError:
                messages.error(request, "กรุณาระบุตัวเลขเปอร์เซ็นต์ที่ถูกต้อง")
            except Exception as e:
                messages.error(request, f"เกิดข้อผิดพลาดในการปรับราคา: {str(e)}")
        else:
            messages.error(request, "กรุณาระบุเปอร์เซ็นต์ที่ต้องการปรับราคา")
    return redirect('medicine_list')
class AppointmentListView(ListView):
    model = Appointment
    template_name = 'myapp/appointment/appointment_list.html'
    context_object_name = 'appointments'
    paginate_by = 10
    def get_queryset(self):
        qs = super().get_queryset().select_related('vet', 'pet', 'pet__owner').annotate(
            vet_full_name=Concat('vet__first_name', Value(' '), 'vet__last_name'),
            owner_full_name=Concat('pet__owner__first_name', Value(' '), 'pet__owner__last_name')
        )
        q = self.request.GET.get('q', '').strip()
        filter_q = models.Q()
        if q:
            q_clean = q
            if q.startswith('หมอ'):
                q_clean = q[3:].strip()
            filter_q = models.Q(pet__name__icontains=q) | \
                       models.Q(service_type__icontains=q) | \
                       models.Q(reason__icontains=q) | \
                       models.Q(ref_no__icontains=q) | \
                       models.Q(vet__first_name__icontains=q_clean) | \
                       models.Q(vet__last_name__icontains=q_clean) | \
                       models.Q(vet__specialization__icontains=q_clean) | \
                       models.Q(owner_full_name__icontains=q) | \
                       models.Q(pet__owner__phone__icontains=q) | \
                       models.Q(pet__owner__customer_id__icontains=q)
            dq = date_search_q(q, field='appointment_date')
            if dq:
                filter_q |= dq
        target_date_str = self.request.GET.get('date')
        if target_date_str:
            try:
                target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
                filter_q &= models.Q(appointment_date=target_date)
            except (ValueError, TypeError):
                pass
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            try:
                filter_q &= models.Q(appointment_date__gte=start_date)
            except (ValueError, TypeError): pass
        if end_date:
            try:
                filter_q &= models.Q(appointment_date__lte=end_date)
            except (ValueError, TypeError): pass
        if filter_q:
            qs = qs.filter(filter_q)
        return qs.order_by('-appointment_date', '-appointment_time')
    def get_context_data(self, **kwargs):
        import json
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        mode = self.request.GET.get('mode', 'list')
        context['mode'] = mode
        target_date_str = self.request.GET.get('date')
        if target_date_str:
            try:
                current_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                current_date = date.today()
        else:
            current_date = date.today()
        context['current_date'] = current_date
        context['prev_date_str'] = (current_date - timedelta(days=1)).isoformat()
        context['next_date_str'] = (current_date + timedelta(days=1)).isoformat()
        context['today_date_str'] = date.today().isoformat()
        context['is_today'] = current_date == date.today()
        qs_all = self.get_queryset()
        events = []
        from django.urls import reverse
        for apt in qs_all:
            if not apt.appointment_date or not apt.appointment_time:
                continue
            color = '#f59e0b'
            if apt.status == 'confirmed': color = '#10b981'
            elif apt.status == 'completed': color = '#3b82f6'
            elif apt.status == 'cancelled': color = '#ef4444'
            events.append({
                'id': apt.id,
                'title': f"{apt.pet.name} - {str(apt.get_status_display())}",
                'start': f"{apt.appointment_date.isoformat()}T{apt.appointment_time.isoformat()}",
                'url': reverse('appointment_detail', kwargs={'pk': apt.pk}),
                'backgroundColor': color,
                'borderColor': color
            })
        context['events_json'] = json.dumps(events)
        return context
class AppointmentDetailView(DetailView):
    model = Appointment
    template_name = 'myapp/appointment/appointment_detail.html'
    context_object_name = 'appointment'
class AppointmentCreateView(CreateView):
    model = Appointment
    template_name = 'myapp/appointment/appointment_form.html'
    form_class = AppointmentForm
    success_url = reverse_lazy('appointment_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from datetime import date
        today = date.today()
        today_apts = Appointment.objects.filter(appointment_date=today).order_by('appointment_time')
        context['today_appointments'] = today_apts
        context['stats'] = {
            'pending': Appointment.objects.filter(status='pending').count(),
            'confirmed': Appointment.objects.filter(status='confirmed').count(),
            'done': Appointment.objects.filter(status='completed').count(),
            'cancelled': Appointment.objects.filter(status='cancelled').count(),
        }
        context['pets_json'] = [
            {
                'id': p.id,
                'name': p.name,
                'species': p.species,
                'owner_name': f"{p.owner.first_name} {p.owner.last_name}" if p.owner else ""
            }
            for p in Pet.objects.select_related('owner').all()
        ]
        return context
class AppointmentUpdateView(UpdateView):
    model = Appointment
    template_name = 'myapp/appointment/appointment_form.html'
    form_class = AppointmentForm
    success_url = reverse_lazy('appointment_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from datetime import date
        today = date.today()
        today_apts = Appointment.objects.filter(appointment_date=today).order_by('appointment_time')
        context['today_appointments'] = today_apts
        context['stats'] = {
            'pending': Appointment.objects.filter(status='pending').count(),
            'confirmed': Appointment.objects.filter(status='confirmed').count(),
            'done': Appointment.objects.filter(status='completed').count(),
            'cancelled': Appointment.objects.filter(status='cancelled').count(),
        }
        context['pets_json'] = [
            {
                'id': p.id,
                'name': p.name,
                'species': p.species,
                'owner_name': f"{p.owner.first_name} {p.owner.last_name}" if p.owner else ""
            }
            for p in Pet.objects.select_related('owner').all()
        ]
        return context
class AppointmentDeleteView(DeleteView):
    model = Appointment
    template_name = 'myapp/core/confirm_delete.html'
    success_url = reverse_lazy('appointment_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        apt = self.get_object()
        context['item_name'] = f"นัดหมาย {apt.pet.name} วันที่ {apt.appointment_date}"
        context['back_url'] = reverse_lazy('appointment_list')
        context['extra_info'] = 'การกระทำนี้ไม่สามารถยกเลิกได้'
        return context
class MedicalRecordListView(ListView):
    model = MedicalRecord
    template_name = 'myapp/medical_record/medical_record_list.html'
    context_object_name = 'records'
    paginate_by = 10
    ordering = ['-visit_date', '-created_at']
    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '')
        if q:
            filter_q = models.Q(pet__name__icontains=q) | \
                       models.Q(ref_no__icontains=q)
            date_query = date_search_q(q, field='visit_date')
            if date_query:
                filter_q |= date_query
            qs = qs.filter(filter_q)
        return qs
class MedicalRecordDetailView(DetailView):
    model = MedicalRecord
    template_name = 'myapp/medical_record/medical_record_detail.html'
    context_object_name = 'record'
class MedicalRecordCreateView(CreateView):
    model = MedicalRecord
    template_name = 'myapp/medical_record/medical_record_form.html'
    form_class = MedicalRecordForm
    success_url = reverse_lazy('medical_record_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "บันทึกประวัติการรักษาใหม่"
        import json
        prices = {m.id: float(m.selling_price) for m in Medicine.objects.all()}
        context['medicine_prices_json'] = json.dumps(prices)
        return context
    def form_valid(self, form):
        response = super().form_valid(form)
        if self.object.pet.price_level == 'ราคาพิเศษ':
            self.object.cost = float(self.object.cost) * 0.9
            self.object.save(update_fields=['cost'])
        return response
class MedicalRecordUpdateView(UpdateView):
    model = MedicalRecord
    template_name = 'myapp/medical_record/medical_record_form.html'
    form_class = MedicalRecordForm
    success_url = reverse_lazy('medical_record_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "แก้ไขประวัติการรักษา"
        import json
        prices = {m.id: float(m.selling_price) for m in Medicine.objects.all()}
        context['medicine_prices_json'] = json.dumps(prices)
        return context
    def form_valid(self, form):
        if self.object.pet.price_level == 'ราคาพิเศษ':
            MedicalRecord.objects.filter(id=self.object.id).update(cost=F('cost') * 0.9)
        from django.shortcuts import redirect
        return redirect(self.get_success_url())
class MedicalRecordDeleteView(DeleteView):
    model = MedicalRecord
    template_name = 'myapp/core/confirm_delete.html'
    success_url = reverse_lazy('medical_record_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        record = self.get_object()
        context['item_name'] = f"ประวัติการรักษา {record.pet.name} วันที่ {record.visit_date}"
        context['back_url'] = reverse_lazy('medical_record_list')
        return context
def medical_history_summary(request):
    query = request.GET.get('q', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    records = MedicalRecord.objects.select_related('pet', 'pet__owner').order_by('-visit_date', '-created_at')
    if query:
        records = records.filter(
            models.Q(pet__name__icontains=query) |
            models.Q(pet__owner__first_name__icontains=query) |
            models.Q(pet__owner__last_name__icontains=query) |
            models.Q(ref_no__icontains=query)
        )
    if date_from:
        records = records.filter(visit_date__gte=date_from)
    if date_to:
        records = records.filter(visit_date__lte=date_to)
    total_visits = records.count()
    total_spending = records.aggregate(total=models.Sum('cost'))['total'] or 0
    last_record = MedicalRecord.objects.order_by('-visit_date').first()
    last_visit_date = last_record.visit_date if last_record else None
    context = {
        'records': records,
        'total_visits': total_visits,
        'total_spending': total_spending,
        'last_visit_date': last_visit_date,
        'query': query,
        'date_from': date_from,
        'date_to': date_to,
        'title': 'สรุปประวัติการรักษาย้อนหลัง'
    }
    return render(request, 'myapp/medical_record/medical_history_summary.html', context)
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
def pos_view(request):
    medicines = Medicine.objects.filter(stock__gt=0).order_by('product_type', 'name')
    pets = Pet.objects.select_related('owner').order_by('name')[:200]
    quick_items = Medicine.objects.filter(
        stock__gt=0,
        product_type__in=['วัคซีน', 'ยาเม็ด', 'ยาน้ำ', 'อาหารเสริม']
    ).order_by('product_type', 'name')[:8]
    medicines_json = []
    for m in medicines:
        medicines_json.append({
            'id': m.id,
            'product_id': m.product_id or '',
            'name': m.name,
            'generic_name': m.generic_name or '',
            'product_type': m.product_type or 'อื่นๆ',
            'selling_price': float(m.selling_price),
            'cost_price': float(m.cost_price or 0),
            'stock': m.stock,
            'unit': m.unit or 'ชิ้น',
            'barcode': m.barcode or '',
            'image': m.image.url if m.image else '',
        })
    pets_json = []
    for p in pets:
        pets_json.append({
            'id': p.id,
            'name': p.name,
            'customer_id': p.customer_id or p.id,
            'owner': f"{p.owner.first_name} {p.owner.last_name}" if p.owner else '',
            'species': p.species,
        })
    unpaid_records = MedicalRecord.objects.filter(is_paid=False, cost__gt=0).select_related('pet')
    unpaid_json = []
    for mr in unpaid_records:
        unpaid_json.append({
            'mr_id': mr.id,
            'pet_id': mr.pet_id,
            'ref_no': mr.ref_no,
            'visit_date': mr.visit_date.strftime('%d/%m/%Y') if mr.visit_date else (mr.created_at.strftime('%d/%m/%Y') if mr.created_at else ''),
            'cost': float(mr.cost),
            'visit_type': mr.visit_type or 'ตรวจสุขภาพทั่วไป',
        })
    context = {
        'medicines': medicines,
        'quick_items': quick_items,
        'pets': pets,
        'medicines_json': json.dumps(medicines_json, ensure_ascii=False),
        'pets_json': json.dumps(pets_json, ensure_ascii=False),
        'unpaid_json': json.dumps(unpaid_json, ensure_ascii=False),
    }
    return render(request, 'myapp/core/pos.html', context)
@require_POST
def pos_checkout(request):
    try:
        data = json.loads(request.body)
        items = data.get('items', [])
        payment_method = data.get('payment_method', 'เงินสด')
        pet_id = data.get('pet_id', None)
        if not items:
            return JsonResponse({'success': False, 'error': 'ไม่มีรายการสินค้า'}, status=400)
        total = Decimal('0')
        sold_items = []
        for item in items:
            if item.get('type') == 'medical_record':
                mr_id = item.get('mr_id')
                try:
                    mr = MedicalRecord.objects.get(id=mr_id)
                    MedicalRecord.objects.filter(id=mr_id).update(is_paid=True)
                    sold_items.append({
                        'name': f"บริการทางการแพทย์ ({mr.visit_type})",
                        'qty': 1,
                        'unit': 'ครั้ง',
                        'price': float(mr.cost),
                        'subtotal': float(mr.cost)
                    })
                    total += mr.cost
                except MedicalRecord.DoesNotExist:
                    pass
                continue
            med_id = item.get('id')
            qty = int(item.get('qty', 1))
            try:
                med = Medicine.objects.get(id=med_id)
                if med.stock < qty:
                    return JsonResponse({
                        'success': False,
                        'error': f'สต็อก {med.name} ไม่เพียงพอ (คงเหลือ {med.stock} {med.unit})'
                    }, status=400)
                line_total = med.selling_price * qty
                total += line_total
                sold_items.append({
                    'name': med.name,
                    'qty': qty,
                    'unit': med.unit or 'ชิ้น',
                    'price': float(med.selling_price),
                    'subtotal': float(line_total),
                })
                med.stock -= qty
                med.save(update_fields=['stock'])
            except Medicine.DoesNotExist:
                return JsonResponse({'success': False, 'error': f'ไม่พบสินค้า ID {med_id}'}, status=400)
        vat_rate = Decimal('0.07')
        vat_amount = total * vat_rate
        grand_total = total + vat_amount
        import random
        receipt_no = f"POS{random.randint(100000, 999999)}"
        return JsonResponse({
            'success': True,
            'receipt_no': receipt_no,
            'payment_method': payment_method,
            'items': sold_items,
            'subtotal': float(total),
            'vat': float(vat_amount),
            'grand_total': float(grand_total),
            'stock_updated': True,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
@login_required
def client_dashboard(request):
    if request.user.is_staff:
        pass
    owner = getattr(request.user, 'owner_profile', None)
    user_pets = []
    upcoming_appointments = []
    if owner:
        user_pets = owner.pets.all()
        today = date.today()
        upcoming_appointments = Appointment.objects.filter(
            pet__owner=owner,
            appointment_date__gte=today,
            status__in=['pending', 'confirmed']
        ).order_by('appointment_date', 'appointment_time')[:5]
    context = {
        'user_pets': user_pets,
        'upcoming_appointments': upcoming_appointments
    }
    return render(request, 'myapp/client/client_dashboard.html', context)
@login_required
def client_register_pet(request):
    owner = getattr(request.user, 'owner_profile', None)
    if not owner:
        messages.info(request, 'กรุณากรอกข้อมูลส่วนตัวก่อนเพื่อลงทะเบียนสัตว์เลี้ยง')
        return redirect('client_profile')
    from .forms import ClientPetRegistrationForm
    if request.method == 'POST':
        form = ClientPetRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            pet = form.save(commit=False)
            pet.owner = owner
            pet.save()
            messages.success(request, 'ลงทะเบียนสัตว์เลี้ยงสำเร็จ!')
            return redirect('client_dashboard')
    else:
        form = ClientPetRegistrationForm()
    return render(request, 'myapp/client/client_register_pet.html', {'form': form, 'owner': owner})
@login_required
def client_edit_pet(request, pk):
    owner = getattr(request.user, 'owner_profile', None)
    if not owner:
        return redirect('client_profile')
    pet = get_object_or_404(Pet, pk=pk, owner=owner)
    from .forms import ClientPetRegistrationForm
    if request.method == 'POST':
        form = ClientPetRegistrationForm(request.POST, request.FILES, instance=pet)
        if form.is_valid():
            pet = form.save(commit=False)
            if request.POST.get('image-clear'):
                if pet.image:
                    pet.image.delete(save=False)
                pet.image = None
            pet.save()
            messages.success(request, 'แก้ไขข้อมูลสัตว์เลี้ยงสำเร็จ!')
            return redirect('client_dashboard')
    else:
        form = ClientPetRegistrationForm(instance=pet)
    return render(request, 'myapp/client/client_edit_pet.html', {'form': form, 'pet': pet, 'owner': owner})
@login_required
def client_profile(request):
    from .forms import ClientProfileForm
    owner = getattr(request.user, 'owner_profile', None)
    if request.method == 'POST':
        form = ClientProfileForm(request.POST, instance=owner)
        if form.is_valid():
            profile = form.save(commit=False)
            if not owner:
                profile.user = request.user
            addr1 = form.cleaned_data.get('address_1', '').strip()
            addr2 = form.cleaned_data.get('address_2', '').strip()
            profile.address = f"{addr1} | {addr2}".strip() if addr1 or addr2 else ""
            profile.save()
            request.user.first_name = profile.first_name
            request.user.last_name = profile.last_name
            request.user.save()
            messages.success(request, 'บันทึกข้อมูลส่วนตัวเรียบร้อยแล้ว!')
            return redirect('client_profile')
    else:
        initial = {}
        if owner:
            if owner.address and " | " in owner.address:
                parts = owner.address.split(" | ", 1)
                initial['address_1'] = parts[0]
                initial['address_2'] = parts[1]
            else:
                initial['address_1'] = owner.address
            form = ClientProfileForm(instance=owner, initial=initial)
        else:
            form = ClientProfileForm(initial={
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
            })
    return render(request, 'myapp/client/client_profile.html', {'form': form, 'owner': owner})
@login_required
def client_appointment(request):
    owner = getattr(request.user, 'owner_profile', None)
    user_pets = owner.pets.all() if owner else []
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'นัดหมายสำเร็จแล้ว!')
            return redirect('client_appointment')
        else:
            messages.error(request, 'กรอกข้อมูลไม่ถูกต้องโปรดตรวจสอบอีกครั้ง')
    else:
        form = AppointmentForm()
    today = date.today()
    if owner:
        today_appointments = Appointment.objects.filter(pet__owner=owner, appointment_date=today).order_by('appointment_time')
        all_apps = Appointment.objects.filter(pet__owner=owner)
    else:
        today_appointments = []
        all_apps = []
    counts = {
        'pending': sum(1 for a in all_apps if a.status == 'pending'),
        'confirmed': sum(1 for a in all_apps if a.status == 'confirmed'),
        'completed': sum(1 for a in all_apps if a.status == 'completed'),
        'cancelled': sum(1 for a in all_apps if a.status == 'cancelled'),
    }
    context = {
        'form': form,
        'user_pets': user_pets,
        'today_appointments': today_appointments,
        'counts': counts
    }
    return render(request, 'myapp/client/client_appointment.html', context)
@login_required
def ajax_execute_scalar(request):
    from django.http import JsonResponse
    from django.db import connection
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Unauthorized access'})
    if request.method == 'POST':
        func_name = request.POST.get('func_name')
        try:
            with connection.cursor() as cursor:
                if func_name == 'fn_CalculatePetAge':
                    birth_date = request.POST.get('birth_date')
                    if not birth_date: return JsonResponse({'success': False, 'error': 'Missing birth_date'})
                    cursor.execute("SELECT (strftime('%Y', 'now') - strftime('%Y', %s)) || ' ปี'", [birth_date])
                    val = cursor.fetchone()
                    result = val[0] if val and val[0] else "N/A"
                    return JsonResponse({'success': True, 'result': result})
                elif func_name == 'fn_FormattedPetName':
                    pet_id = request.POST.get('pet_id')
                    cursor.execute("SELECT name || ' (' || species || ')' FROM myapp_pet WHERE id = %s", [pet_id])
                    result = cursor.fetchone()[0]
                    return JsonResponse({'success': True, 'result': result})
                elif func_name == 'fn_GetMedicineStockValue':
                    cursor.execute("SELECT SUM(stock * selling_price) FROM myapp_medicine")
                    result = cursor.fetchone()[0]
                    return JsonResponse({'success': True, 'result': float(result) if result else 0.0})
                elif func_name == 'fn_GetPetVisitCount':
                    pet_id = request.POST.get('pet_id')
                    cursor.execute("SELECT COUNT(*) FROM myapp_medicalrecord WHERE pet_id = %s", [pet_id])
                    result = cursor.fetchone()[0]
                    return JsonResponse({'success': True, 'result': result})
                elif func_name == 'fn_GetTotalSpending':
                    owner_id = request.POST.get('owner_id')
                    cursor.execute("SELECT SUM(cost) FROM myapp_medicalrecord mr JOIN myapp_pet p ON mr.pet_id = p.id WHERE p.owner_id = %s", [owner_id])
                    result = cursor.fetchone()[0]
                    return JsonResponse({'success': True, 'result': float(result) if result else 0.0})
                elif func_name == 'sp_GetMonthlyRevenue':
                    year, month = request.POST.get('year'), request.POST.get('month')
                    total = MedicalRecord.objects.filter(visit_date__year=year, visit_date__month=month).aggregate(total=models.Sum('cost'))['total'] or 0
                    return JsonResponse({'success': True, 'result': float(total)})
                elif func_name == 'fn_GetTotalClinicRevenue':
                    total = MedicalRecord.objects.aggregate(total=models.Sum('cost'))['total'] or 0
                    return JsonResponse({'success': True, 'result': float(total)})
                elif func_name == 'update_phone_via_view':
                    owner_id, new_phone = request.POST.get('owner_id'), request.POST.get('new_phone')
                    print(f"DEBUG SQL: Updating OwnerID={owner_id} to Phone={new_phone}")
                    cursor.execute("UPDATE v_ClinicDashboard SET OwnerPhone = %s WHERE OwnerID = %s", [new_phone, owner_id])
                    return JsonResponse({'success': True, 'message': 'อัปเดตเบอร์โทรผ่าน View (SQLite Trigger) สำเร็จ'})
                elif func_name == 'update_pet_name_via_view':
                    pet_id, new_pet_name = request.POST.get('pet_id'), request.POST.get('new_pet_name')
                    print(f"DEBUG SQL: Updating PetInternalID={pet_id} to Name={new_pet_name}")
                    cursor.execute("UPDATE v_ClinicDashboard SET PetName = %s WHERE PetInternalID = %s", [new_pet_name, pet_id])
                    return JsonResponse({'success': True, 'message': 'อัปเดตชื่อสัตว์ผ่าน View (SQLite Trigger) สำเร็จ'})
                elif func_name == 'update_vet_hours_via_view':
                    vet_id, new_hours = request.POST.get('vet_id'), request.POST.get('new_hours')
                    cursor.execute("UPDATE v_VetWorkload SET working_hours = %s WHERE vet_id = %s", [new_hours, vet_id])
                    return JsonResponse({'success': True, 'message': 'อัปเดตชั่วโมงปฏิบัติงานผ่าน View (SQLite Trigger) สำเร็จ'})
                else:
                    return JsonResponse({'success': False, 'error': 'Unknown function mapping'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def ajax_get_breeds(request):
    species = request.GET.get('species', '')
    if species:
        breeds = Pet.objects.filter(species=species).exclude(breed__isnull=True).exclude(breed__exact='').values_list('breed', flat=True).distinct()
        return JsonResponse({'breeds': list(breeds)})
    return JsonResponse({'breeds': []})

def ajax_get_all_species(request):
    species_list = Pet.objects.exclude(species__isnull=True).exclude(species__exact='').values_list('species', flat=True).distinct()
    return JsonResponse({'species': list(species_list)})

def ajax_get_all_breeds(request):
    breed_list = Pet.objects.exclude(breed__isnull=True).exclude(breed__exact='').values_list('breed', flat=True).distinct()
    return JsonResponse({'breeds': list(breed_list)})