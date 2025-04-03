
def get_default_category():
    from .models import Category
    category, created = Category.objects.get_or_create(
        name="Uncategorized",
        defaults={'image': ''}  # Provide a default image if needed
    )
    return category