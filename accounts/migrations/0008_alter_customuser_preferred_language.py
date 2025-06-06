# Generated by Django 5.2 on 2025-05-17 01:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_customuser_preferred_language'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='preferred_language',
            field=models.CharField(choices=[('en', 'English'), ('sw', 'Swahili'), ('yo', 'Yoruba'), ('ha', 'Hausa'), ('zu', 'Zulu'), ('ig', 'Igbo'), ('fr', 'French')], default='en', max_length=5),
        ),
    ]
