import re
from django.shortcuts import redirect
from django.urls import reverse
from django.core.exceptions import PermissionDenied
class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.exceptions = [
            re.compile(r'^/login/.*$'),
            re.compile(r'^/register/.*$'),
            re.compile(r'^/admin/.*$'),
            re.compile(r'^/static/.*$'),
            re.compile(r'^/media/.*$'),
        ]
        self.admin_only_paths = [
            re.compile(r'^/pets/.*$'),
            re.compile(r'^/owners/.*$'),
            re.compile(r'^/vets/.*$'),
            re.compile(r'^/medicines/.*$'),
            re.compile(r'^/appointments/.*$'),
            re.compile(r'^/records/.*$'),
            re.compile(r'^/pos/.*$'),
            re.compile(r'^/admin-backend/.*$'),
        ]
    def __call__(self, request):
        path = request.path_info
        for pattern in self.exceptions:
            if pattern.match(path):
                return self.get_response(request)
        if not request.user.is_authenticated:
            return redirect(reverse('login'))
        is_admin_path = any(pattern.match(path) for pattern in self.admin_only_paths)
        if is_admin_path and not request.user.is_staff:
            from django.contrib import messages
            messages.warning(request, "ขออภัย! คุณไม่มีสิทธิ์เข้าถึงหน้านี้ (เฉพาะพนักงาน)")
            return redirect('client_dashboard')
        return self.get_response(request)
from django.db import connection
ROLE_TO_DB_USER = {
    'staff': 'Staff_User1',
}
class SQLServerSecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        db_user = None
        if request.user.is_authenticated:
            if request.user.is_superuser:
                db_user = None
            elif request.user.is_staff:
                db_user = ROLE_TO_DB_USER['staff']
            if db_user:
                try:
                    with connection.cursor() as cursor:
                        cursor.execute(f"EXECUTE AS USER = '{db_user}';")
                except Exception as e:
                    print(f"[SQLServerSecurity] Impersonate error: {e}")
        response = self.get_response(request)
        if request.user.is_authenticated and db_user:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("REVERT;")
            except Exception:
                pass
        return response