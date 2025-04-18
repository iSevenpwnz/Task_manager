from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

from .models import VerificationCode
from .forms import RegisterForm, VerificationForm


class LoginView(View):
    template_name = 'tasks/auth/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            messages.success(request, f"Вітаємо, {user.username}!")
            return redirect(next_url)
        else:
            messages.error(request, "Неправильне ім'я користувача або пароль")
            return render(request, self.template_name)


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        return redirect('login')

    def post(self, request):
        logout(request)
        messages.info(request, "Ви вийшли з системи")
        return redirect('login')


class RegisterView(View):
    template_name = 'tasks/auth/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        form = RegisterForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            email = form.cleaned_data.get('email')
            code = VerificationCode.generate_code()
            verification = VerificationCode.objects.create(
                user=user,
                code=code,
                email=email
            )

            subject = 'Підтвердження реєстрації'
            context = {
                'user': user,
                'code': code
            }
            html_message = render_to_string('tasks/email/verification.html', context)
            plain_message = strip_tags(html_message)
            from_email = settings.DEFAULT_FROM_EMAIL

            send_mail(
                subject,
                plain_message,
                from_email,
                [email],
                html_message=html_message,
                fail_silently=False,
            )

            messages.success(request, "Реєстрація успішна! Увійдіть, використовуючи ваші облікові дані.")
            return redirect('login')
        return render(request, self.template_name, {'form': form})


class VerifyCodeView(View):
    template_name = 'tasks/auth/verify_code.html'

    def get(self, request):
        form = VerificationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = VerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            return redirect('login')
        return render(request, self.template_name, {'form': form})
