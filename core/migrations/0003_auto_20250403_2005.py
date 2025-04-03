from django.db import migrations

def create_uncategorized_category(apps, schema_editor):
    Category = apps.get_model('core', 'Category')
    Category.objects.get_or_create(name="Uncategorized", defaults={'image': ''})

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0002_alter_professional_location_and_more'),  # Replace with your last migration
    ]

    operations = [
        migrations.RunPython(create_uncategorized_category, migrations.RunPython.noop),
    ]