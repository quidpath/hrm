from django.db import migrations


class Migration(migrations.Migration):
    """No-op: already applied on prod DB from prior deployment."""

    dependencies = [
        ('payroll', '0001_initial'),
    ]

    operations = []
