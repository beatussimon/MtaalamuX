# Generated migration for Consultation and AvailabilitySlot constraints
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_availabilityslot'),
    ]

    operations = [
        # Add unique constraint to AvailabilitySlot
        migrations.AddConstraint(
            model_name='availabilityslot',
            constraint=models.UniqueConstraint(
                fields=['expert', 'start_time', 'end_time'],
                name='unique_expert_slot_time'
            ),
        ),
        
        # Add availability FK to Consultation with unique constraint
        migrations.AddField(
            model_name='consultation',
            name='availability',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='consultations',
                to='core.availabilityslot',
                unique=True
            ),
        ),
        
        # Add unique constraint to prevent overlapping consultations
        migrations.AddConstraint(
            model_name='consultation',
            constraint=models.UniqueConstraint(
                fields=['client', 'expert', 'start_time'],
                name='unique_client_expert_consultation',
                condition=models.Q(start_time__isnull=False)
            ),
        ),
    ]
