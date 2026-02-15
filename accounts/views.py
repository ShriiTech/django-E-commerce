import random
from datetime import timedelta

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View

from .forms import LoginForm, CustomUserRegistrationForm , VerifyCodeForm , LoginVerifyForm
from accounts.utils import send_otp_code
from .models import OtpCode, CustomUser
from django.contrib import messages
from django.utils import timezone

import logging
from django.contrib.auth import login
logger = logging.getLogger('accounts')


class CustomUserRegisterView (View):
    form_class = CustomUserRegistrationForm
    template_name = 'register.html'

    def get (self, request):
        form = self.form_class
        return render(request, self.template_name, {'form':form})
    

    def post (self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            random_code = random.randint(1000, 9999)
            send_otp_code(form.cleaned_data['phone_number'], random_code)
            OtpCode.objects.create(phone_number = form.cleaned_data['phone_number'], code = random_code)
            request.session['user_registeration_info'] = {
                'phone_number' : form.cleaned_data['phone_number'],
                'email' : form.cleaned_data['email'],
                'full_name' : form.cleaned_data['full_name'],
                'password' : form.cleaned_data['password'],
            }

            request.session['otp_type'] = 'register'

            messages.success(request, 'we sent you a code', 'success')
            return redirect('accounts:verify_code')
        return render (request , self.template_name , {'form':form})


class CustomUserRegisterVerifyCodeView(View):
    form_class = VerifyCodeForm

    def get(self, request):
        form = self.form_class()
        return render (request , 'verify.html', {'form': form})

    def post(self, request):
        user_session = request.session.get('user_registeration_info')

        if not user_session:
            messages.error(request, 'لطفاً دوباره ثبت‌نام کنید')
            return redirect('accounts:user_register')

        # ✅ ساخت فرم
        form = self.form_class(request.POST)

        if not form.is_valid():
            return render(request, 'verify.html', {'form': form})

        cd = form.cleaned_data

        # ✅ گرفتن OTP از دیتابیس
        code_instance = OtpCode.objects.filter(
            phone_number=user_session['phone_number']
        ).first()

        if not code_instance:
            messages.error(request, 'کدی برای شما یافت نشد')
            return redirect('accounts:verify_code')

        if cd['code'] != code_instance.code:
            messages.error(request, 'کد وارد شده اشتباه است')
            return render(request, 'verify.html', {'form': form})
        
        expiration_time = code_instance.created + timedelta(minutes=2)
        if timezone.now() > expiration_time:
                code_instance.delete()
                messages.error(request, 'کد شما منقضی شده است')
                return redirect('accounts:verify_code')
        
                # ✅ ساخت کاربر
        user = CustomUser.objects.create(
            phone_number=user_session['phone_number'],
            email=user_session['email'],
            full_name=user_session['full_name'],
        )
        user.set_password(user_session['password'])
        user.save()

        # لاگین خودکار بعد از ثبت‌نام
        login(request, user)

        code_instance.delete()

        request.session.pop('user_registeration_info', None)
        
        messages.success(request, 'ثبت‌نام با موفقیت انجام شد')
        return redirect('home:home')



class LoginView(View):
    form_class = LoginForm
    template_name = 'login.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)

        if not form.is_valid():
            return render(request, self.template_name, {'form': form})

        phone_number = form.cleaned_data['phone_number']
        random_code = random.randint(1000, 9999)

        send_otp_code(phone_number, random_code)

        OtpCode.objects.create(
            phone_number=phone_number,
            code=random_code
        )

        request.session['user_login_info'] = {
            'phone_number': phone_number,
        }
        
        messages.success(request, 'کد ورود برای شما ارسال شد')
        return redirect('accounts:verify_login')


class LoginVerify(View):
    form_class = LoginVerifyForm
    template_name = 'verify_login.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        phone_number = request.session.get('user_login_info', {}).get('phone_number')

        if not phone_number:
            messages.error(request, 'اطلاعات کاربر پیدا نشد.')
            return redirect('accounts:verify_login')

        if form.is_valid():
            code = form.cleaned_data['code']

            code_instance = OtpCode.objects.filter(phone_number=phone_number, code=code).first()

            if code_instance:
                # بررسی منقضی شدن OTP (2 دقیقه اعتبار)
                expiration_time = code_instance.created + timedelta(minutes=2)
                if timezone.now() > expiration_time:
                    code_instance.delete()
                    messages.error(request, 'کد شما منقضی شده است. لطفاً دوباره OTP دریافت کنید.')
                    return redirect('accounts:verify_login')

                # لاگین موفق
                try:
                    user = CustomUser.objects.get(phone_number=phone_number)
                    login(request, user)
                except CustomUser.DoesNotExist:
                    messages.error(request, 'کاربر پیدا نشد.')
                    return redirect('accounts:login')

                code_instance.delete()  # حذف OTP بعد از ورود موفق
                messages.success(request, 'با موفقیت وارد شدید.', 'success')
                return redirect('home:home')

            messages.error(request, 'کد وارد شده نادرست است.')

        else:
            messages.error(request, 'فرم معتبر نیست.')

        return render(request, self.template_name, {'form': form})
