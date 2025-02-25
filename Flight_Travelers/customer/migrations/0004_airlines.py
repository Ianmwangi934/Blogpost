# Generated by Django 4.2.3 on 2025-02-17 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0003_alter_profile_passport_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='Airlines',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('country', models.CharField(blank=True, max_length=100, null=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='profile/')),
            ],
        ),
    ]
