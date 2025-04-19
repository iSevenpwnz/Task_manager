import logging
from django.http import HttpResponseServerError
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.contrib import messages

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        logger.exception("Серверна помилка: %s", str(exception))
        
        # Перевіряємо, чи це запит на реєстрацію
        if request.path == '/register/' and request.method == 'POST':
            # Додаємо повідомлення про помилку і перенаправляємо на домашню сторінку
            messages.error(request, "Виникла помилка при реєстрації. Спробуйте пізніше або зверніться до адміністратора.")
            return redirect('home')
        
        return HttpResponseServerError("Серверна помилка. Спробуйте пізніше.") 