# Generated manually for renaming professional tier

from django.db import migrations

def rename_professional_tier(apps, schema_editor):
    UserProfile = apps.get_model('core', 'UserProfile')
    # Rename 'plus' to 'professional' in existing data
    UserProfile.objects.filter(tier='plus').update(tier='professional')

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(rename_professional_tier),
    ]
