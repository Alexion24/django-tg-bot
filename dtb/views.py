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

from django.contrib.auth.models import User
from users.models import User
from users.forms import CreateUserForm, BroadcastForm
from tg_users.models import WebhookMessage, TgUser
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
        u_id = uuid.uuid4()
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        user.u_id = u_id
        user.save()
        data = {
            "start": f"https://t.me/django_celery_test_bot?start={u_id}",
            "get_unique_key": f'Ваш уникальный ключ: {u_id}'
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
        users = User.objects.all()
        for u in users:
            TelegramBotWebhookView.send_message(
                f'Hello, {u.username}!\n{request.POST.get("broadcast_text")}',
                u.chat_id
            )

        return HttpResponseRedirect(reverse_lazy("profile"))


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

    def post(self, request, *args, **kwargs):

        t_data = json.loads(request.body)
        print(json.dumps(t_data))
        WebhookMessage.objects.create(payload=json.dumps(t_data))
        response = {"ok": "POST request processed"}

        if t_data.get('message'):
            t_message = t_data["message"]
            t_chat = t_message["chat"]
            text = t_message["text"].strip().lower()
        else:
            return JsonResponse(response)

        text = text.lstrip('/')
        chat = t_chat["id"]
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
            self.user_check(text, chat)

        return JsonResponse(response)

    def user_check(self, text, chat):

        try:
            user = User.objects.get(u_id=text)
            user.chat_id = chat
            user.save()
            msg = "You successfully registered!"
            self.send_message(msg, chat)
        except User.DoesNotExist:
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
