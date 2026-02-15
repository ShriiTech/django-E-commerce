from django import forms
from .models import CustomUser, OtpCode
from django.contrib.auth.forms import ReadOnlyPasswordHashField


class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('email', 'phone_number', 'full_name')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd.get('password1') and cd.get('password2') and cd['password1'] != cd['password2']:
            raise forms.ValidationError("Passwords don't match")
        return cd['password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class CustomUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(
        help_text="You can change password using <a href=\"../password\">this form</a>"
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'phone_number', 'full_name', 'password', 'last_login')


class CustomUserRegistrationForm(forms.Form):
    email = forms.EmailField()
    full_name = forms.CharField()
    phone_number = forms.CharField(max_length=11)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data['email']
        user = CustomUser.objects.filter(email = email).exists()
        if user :
            raise forms.ValidationError ("this email already exist.")
        return email
    
    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number']
        user = CustomUser.objects.filter(phone_number = phone).exists()
        if user:
            raise forms.ValidationError('this phone number already exist')
        OtpCode.objects.filter(phone_number = phone).delete
        return phone
        

class VerifyCodeForm(forms.Form):
    code = forms.IntegerField()


class LoginForm(forms.Form):
    phone_number = forms.CharField(
        max_length=11,
        label='شماره موبایل',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '09xxxxxxxxx'
        })
    )

    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number']

        if not phone.isdigit():
            raise forms.ValidationError('شماره موبایل فقط باید شامل عدد باشد')

        if not phone.startswith('09'):
            raise forms.ValidationError('شماره موبایل معتبر نیست')

        if len(phone) != 11:
            raise forms.ValidationError('شماره موبایل باید ۱۱ رقم باشد')

        if not CustomUser.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError('کاربری با این شماره وجود ندارد')

        return phone


class LoginVerifyForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'کد تایید را وارد کنید',
            'class': 'form-control'
        }),
        label='کد تایید'
    )
    
