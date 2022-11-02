import json
import logging
import requests
import uuid

from django.shortcuts import render
from django.views import View
from django.http import JsonResponse, HttpResponseRedirect
from django.views.generic import ListView, CreateView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.urls import reverse_lazy

from tg_bot.forms import RegistrationForm, BroadcastForm
from tg_bot.models import WebhookMessage, TgUser
from dtb.settings import TELEGRAM_TOKEN


logger = logging.getLogger(__name__)
TELEGRAM_URL = "https://api.telegram.org/bot"
PROFILE_URL = 'https://8bc6-46-146-120-138.eu.ngrok.io/profile/'


class IndexView(TemplateView):

    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        return render(request, template_name=self.template_name)


class ProfileView(TemplateView):

    template_name = 'profile.html'

    def get(self, request, *args, **kwargs):
        tg_key = uuid.uuid4()
        user_id = request.user.id
        user = TgUser.objects.get(id=user_id)
        user.tg_key = tg_key
        user.save()
        data = {
            "start": f"https://t.me/django_celery_test_bot?start={tg_key}",
            "get_unique_key": f'Ваш уникальный ключ: {tg_key}'
        }
        return render(request, template_name=self.template_name, context=data)


class BroadcastMessageView(TemplateView):

    template_name = 'admin/broadcast_message.html'
    form_class = BroadcastForm
    success_url = reverse_lazy('profile')

    def get(self, request, *args, **kwargs):
        return render(
            request,
            template_name=self.template_name,
            context={
                'Title': 'Broadcast message',
                'form': self.form_class,
                'button_text': 'Send message'
            }
        )

    def post(self, request, *args, **kwargs):
        users = TgUser.objects.all()
        for u in users:
            TelegramBotWebhookView.send_message(
                f'Hello, {u.username}!\n{request.POST.get("broadcast_text")}',
                u.chat_id
            )

        return HttpResponseRedirect(reverse_lazy("profile"))


class RegisterUserView(SuccessMessageMixin, CreateView):

    model = TgUser
    template_name = 'form.html'
    form_class = RegistrationForm
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

    def post(self, request, *args, **kwargs):

        tg_data = json.loads(request.body)
        print(json.dumps(tg_data))
        WebhookMessage.objects.create(payload=json.dumps(tg_data))
        response = {"ok": "POST request processed"}

        if tg_data.get('message'):
            tg_message = tg_data["message"]
            tg_chat = tg_message["chat"]
            text = tg_message["text"].strip().lower()
            tg_id = tg_message["from"]["id"]
            tg_username = tg_message["from"]["username"]
        else:
            return JsonResponse(response)

        text = text.lstrip('/')
        chat = tg_chat["id"]
        text_is_u_id = False

        if text.startswith('start') and len(text) > 10:
            _, text = text.split()

            if text.count('-') == 4:
                text_is_u_id = True
            else:
                msg = f"Please get your unique key, visit {PROFILE_URL}"
                self.send_message(msg, chat)
        elif text.count('-') == 4:
            text_is_u_id = True

        if text_is_u_id:
            self.get_user_data(tg_id, tg_username, text, chat)

        return JsonResponse(response)

    def get_user_data(self, tg_id, tg_username, text, chat):
        if user := TgUser.objects.get(tg_key=text):
            user.chat_id = chat
            user.tg_id = tg_id
            user.tg_username = tg_username
            user.save()
            msg = "You successfully registered!"
            self.send_message(msg, chat)
        else:
            msg = f"Wrong unique key!\nPlease get your unique key, visit {PROFILE_URL}"
            self.send_message(msg, chat)

    @staticmethod
    def send_message(message, chat_id):
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }
        response = requests.post(
            f"{TELEGRAM_URL}{TELEGRAM_TOKEN}/sendMessage", data=data
        )

    def get(self, request, *args, **kwargs):  # for debug
        return JsonResponse({"ok": "Get request received! But nothing done"})


class WebhookListView(ListView):

    model = WebhookMessage
    template_name = 'webhook/webhook.html'
    success_url = reverse_lazy('webhook-message-list')
    context_object_name = 'webhook'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Webhook'
        return context
