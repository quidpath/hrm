from django.db import migrations


class Migration(migrations.Migration):
    """No-op: already applied on prod DB from prior deployment."""

    dependencies = [
        ('recruitment', '0003_jobposting_safe_columns'),
    ]

    operations = []
