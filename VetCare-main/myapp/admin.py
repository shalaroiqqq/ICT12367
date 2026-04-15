from django.contrib import admin
from .models import Owner, Pet, Vet, Medicine, Appointment, MedicalRecord
@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone', 'address')
    search_fields = ('first_name', 'last_name', 'phone')
    list_filter = ('last_name',)
@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'species', 'breed', 'owner', 'birth_date')
    search_fields = ('name', 'owner__first_name', 'owner__last_name')
    list_filter = ('species', 'owner')
@admin.register(Vet)
class VetAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'specialization', 'phone')
    search_fields = ('first_name', 'last_name', 'specialization')
    list_filter = ('specialization',)
@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'stock', 'description')
    search_fields = ('name',)
    list_filter = ('stock',)
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('pet', 'vet', 'appointment_date', 'appointment_time', 'reason')
    search_fields = ('pet__name', 'vet__first_name', 'vet__last_name')
    list_filter = ('appointment_date', 'vet')
@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('pet', 'vet', 'diagnosis', 'cost', 'created_at')
    search_fields = ('pet__name', 'vet__first_name', 'vet__last_name', 'diagnosis')
    list_filter = ('created_at', 'vet')
    readonly_fields = ('created_at',)