from users.models import Customer; for c in Customer.objects.all(): print(c.user.username, c.user.email, c.identity_document)
