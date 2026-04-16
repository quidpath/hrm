from django.db import migrations


class Migration(migrations.Migration):
    """No-op: already applied on prod DB from prior deployment."""

    dependencies = [
        ('payroll', '0002_payrollrun_drafted_at_payrollrun_posted_at_and_more'),
    ]

    operations = []
