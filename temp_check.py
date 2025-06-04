from products.models import Category; [print(c.id, c.name, c.description) for c in Category.objects.all()]
