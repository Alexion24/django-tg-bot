from django.contrib import admin

from tg_bot.models import TgUser, WebhookMessage

admin.site.register(WebhookMessage)


@admin.register(TgUser)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'tg_key', 'username', 'tg_username', 'chat_id', 'created_at'
    ]
    search_fields = ('username', 'user_id')

    actions = ['broadcast']

