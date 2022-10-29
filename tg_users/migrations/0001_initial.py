# Generated by Django 3.2.9 on 2022-10-29 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TgUser',
            fields=[
                ('created_at', models.DateTimeField(auto_now=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('user_id', models.PositiveBigIntegerField(primary_key=True, serialize=False)),
                ('username', models.CharField(blank=True, max_length=32, null=True)),
                ('first_name', models.CharField(max_length=256)),
                ('last_name', models.CharField(blank=True, max_length=256, null=True)),
                ('language_code', models.CharField(blank=True, help_text="Telegram client's lang", max_length=8, null=True)),
                ('deep_link', models.CharField(blank=True, max_length=64, null=True)),
                ('is_blocked_bot', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('-created_at',),
                'abstract': False,
            },
        ),
    ]