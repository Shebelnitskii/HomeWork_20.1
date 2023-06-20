import random

from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.utils.crypto import get_random_string
from django.views import View
from django.views.generic import CreateView, UpdateView
from config import settings
from users.forms import UserRegisterForm, UserProfileForm
from users.models import User, EmailVerification


# Create your views here.

class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        recipient_email = form.save()

        # Создаем объект EmailVerification
        email_verification = EmailVerification(user=recipient_email)
        email_verification.token = get_random_string(length=32)  # Генерируем уникальный токен
        email_verification.save()

        # Отправляем письмо с ссылкой на верификацию
        verification_url = self.request.build_absolute_uri(
            reverse('users:verify_email', args=[email_verification.token]))
        message = f'Вы успешно зарегистрировались на нашей платформе. Подтвердите свою почту, перейдя по ссылке: {verification_url}'
        send_mail(
            subject='Поздравляем с регистрацией',
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[recipient_email.email],
            fail_silently=False)

        return super().form_valid(form)

class EmailVerificationView(View):
    def get(self, request, token):
        try:
            email_verification = EmailVerification.objects.get(token=token)
            user = email_verification.user
            user.is_active = True  # Активируем пользователя
            user.save()
            email_verification.delete()  # Удаляем объект EmailVerification
            return redirect('users:login')  # Редирект на страницу входа
        except EmailVerification.DoesNotExist:
            return HttpResponse('Ошибка верификации')  # Отображаем сообщение об ошибке

class ProfileView(UpdateView):
    model = User
    form_class = UserProfileForm
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user

def reset_password(request):
    new_password = ''.join([str(random.randint(0, 9)) for _ in range(12)])
    send_mail(
        subject='Сброс пароля',
        message= f'Ваш новый пароль: {new_password}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[request.user.email])
    request.user.set_password(new_password)
    request.user.save()
    return redirect(reverse('main:category_list'))



