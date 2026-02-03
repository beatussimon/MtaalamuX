"""Migration to add consultation fields and time-bound messaging support"""
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_professional_allow_instant_messaging'),
    ]

    operations = [
        # Add start_time and end_time to Consultation
        migrations.AddField(
            model_name='consultation',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='consultation',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        
        # Add consultation foreign key to Conversation
        migrations.AddField(
            model_name='conversation',
            name='consultation',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='conversations',
                to='core.consultation'
            ),
        ),
    ]
