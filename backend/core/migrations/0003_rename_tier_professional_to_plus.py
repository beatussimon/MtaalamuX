"""
Migration to rename 'professional' tier to 'plus' tier.
This ensures backward compatibility by updating existing tier values.
"""
from django.db import migrations

def rename_tier_values(apps, schema_editor):
    """Rename all 'professional' tier values to 'plus'"""
    UserProfile = apps.get_model('core', 'UserProfile')
    UpgradeRequest = apps.get_model('core', 'UpgradeRequest')
    
    # Update UserProfile tier values
    UserProfile.objects.filter(tier='professional').update(tier='plus')
    
    # Update UpgradeRequest upgrade_type values
    UpgradeRequest.objects.filter(upgrade_type='professional').update(upgrade_type='plus')

def reverse_tier_values(apps, schema_editor):
    """Reverse the tier value changes"""
    UserProfile = apps.get_model('core', 'UserProfile')
    UpgradeRequest = apps.get_model('core', 'UpgradeRequest')
    
    # Update UserProfile tier values (revert)
    UserProfile.objects.filter(tier='plus').update(tier='professional')
    
    # Update UpgradeRequest upgrade_type values (revert)
    UpgradeRequest.objects.filter(upgrade_type='plus').update(upgrade_type='professional')

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0002_rename_professional_tier'),
    ]

    operations = [
        migrations.RunPython(rename_tier_values, reverse_tier_values),
    ]
