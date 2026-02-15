from django.contrib import messages

from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect


class IsAdminUserMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin
    
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and getattr(user, 'is_admin', False)

    # ✅ اگر دسترسی نداشت
    def handle_no_permission(self):
        user = self.request.user
        if not user.is_authenticated:
            # اگر کاربر لاگین نکرده بود → ریدایرکت به login
            return redirect(self.login_url)
        
        # اگر کاربر لاگین کرده ولی ادمین نیست → پیام و redirect
        messages.error(self.request, "شما دسترسی به این صفحه را ندارید")
        return redirect('home:home')
