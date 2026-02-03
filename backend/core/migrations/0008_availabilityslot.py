# Generated migration for AvailabilitySlot model
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('core', '0007_add_consultation_to_conversation'),
    ]

    operations = [
        migrations.CreateModel(
            name='AvailabilitySlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('is_booked', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('booked_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='booked_slots', to='auth.user')),
                ('expert', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availability_slots', to='core.professional')),
            ],
            options={
                'verbose_name': 'Availability Slot',
                'verbose_name_plural': 'Availability Slots',
                'ordering': ['start_time'],
            },
        ),
    ]
