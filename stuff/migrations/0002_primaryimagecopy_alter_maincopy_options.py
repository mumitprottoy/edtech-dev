# Generated by Django 5.0.6 on 2024-10-23 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stuff', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrimaryImageCopy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.TextField()),
            ],
        ),
        migrations.AlterModelOptions(
            name='maincopy',
            options={'verbose_name_plural': 'Main Copies'},
        ),
    ]
