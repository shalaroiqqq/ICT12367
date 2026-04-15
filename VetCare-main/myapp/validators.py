from django.core.exceptions import ValidationError
class CustomPasswordValidator:
    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError('รหัสผ่านสั้นเกินไป ต้องมีอย่างน้อย 8 ตัวอักษร', code='password_too_short')
        if password.isdigit():
            raise ValidationError('รหัสผ่านต้องไม่เป็นตัวเลขทั้งหมด', code='password_entirely_numeric')
        common_passwords = ['12345678', 'password', 'qwertyui', '11111111', '123456789']
        if password.lower() in common_passwords:
            raise ValidationError('รหัสผ่านนี้เดาง่ายเกินไป กรุณาเปลี่ยนใหม่', code='password_too_common')
    def get_help_text(self):
        return 'รหัสผ่านต้องมีความยาวอย่างน้อย 8 ตัวอักษร และไม่เป็นตัวเลขทั้งหมด'