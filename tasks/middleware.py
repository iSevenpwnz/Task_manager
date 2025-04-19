import logging
from django.http import HttpResponseServerError
from django.template.response import TemplateResponse

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
            return TemplateResponse(
                request, 
                'registration/register.html',
                {'error': 'Виникла помилка при реєстрації. Перевірте правильність введених даних.'}
            )
        
        return HttpResponseServerError("Серверна помилка. Спробуйте пізніше.") 