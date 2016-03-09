# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-09 00:16
from __future__ import unicode_literals

import api.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(choices=[(b'pending', b'pending'), (b'started', b'started'), (b'finished', b'finished'), (b'failed', b'failed')], default=b'pending', editable=False, max_length=10)),
                ('public', models.BooleanField(default=False)),
                ('notify', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('input', models.FileField(db_index=True, upload_to=api.models.user_dir, validators=[api.models.file_size_validator])),
                ('results', models.FileField(db_index=True, editable=False, null=True, upload_to=api.models.user_dir)),
                ('result_id', models.CharField(editable=False, max_length=36, null=True)),
                ('error', models.TextField(editable=False, null=True)),
                ('owner', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
