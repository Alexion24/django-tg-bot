import json
import logging
from django.views import View
from django.http import JsonResponse
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.urls import reverse_lazy
from telegram import Update

from dtb.celery import app
from dtb.settings import DEBUG
from tgbot.dispatcher import dispatcher
from tgbot.main import bot

from users.models import User
from users.forms import CreateUserForm

logger = logging.getLogger(__name__)


@app.task(ignore_result=True)
def process_telegram_event(update_json):
    update = Update.de_json(update_json, bot)
    dispatcher.process_update(update)


class IndexView(TemplateView):

    template_name = 'index.html'


class CreateUserView(SuccessMessageMixin, CreateView):

    model = User
    template_name = 'form.html'
    form_class = CreateUserForm
    success_url = reverse_lazy('login')
    success_message = 'User successfully registered.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Registration'
        context['button_text'] = 'Register'
        return context


class LoginUserView(SuccessMessageMixin, LoginView):

    template_name = 'form.html'
    success_message = 'You logged in'
    next_page = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Log in'
        context['button_text'] = 'Login'
        return context


class LogoutUserView(SuccessMessageMixin, LogoutView):

    next_page = reverse_lazy('index')

    def dispatch(self, request, *args, **kwargs):
        messages.add_message(
            request,
            messages.INFO,
            'You logged out'
        )
        return super().dispatch(request, *args, **kwargs)


class TelegramBotWebhookView(View):
    # WARNING: if fail - Telegram webhook will be delivered again.
    # Can be fixed with async celery task execution
    def post(self, request, *args, **kwargs):
        if DEBUG:
            process_telegram_event(json.loads(request.body))
        else:
            # Process Telegram event in Celery worker (async)
            # Don't forget to run it and & Redis (message broker for Celery)!
            # Locally, You can run all of these services via docker-compose.yml
            process_telegram_event.delay(json.loads(request.body))

        # e.g. remove buttons, typing event
        return JsonResponse({"ok": "POST request processed"})

    def get(self, request, *args, **kwargs):  # for debug
        return JsonResponse({"ok": "Get request received! But nothing done"})
