from django.db import migrations


class Migration(migrations.Migration):
    """No-op: already applied on prod DB from prior deployment."""

    dependencies = [
        ('payroll', '0003_payrollrun_safe_columns'),
    ]

    operations = []
