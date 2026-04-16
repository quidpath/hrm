from django.db import migrations


class Migration(migrations.Migration):
    """
    This migration was previously applied with AddField operations.
    Replaced with a no-op to avoid duplicate column errors on databases
    where the columns already exist from a prior deployment.
    The actual columns are added safely in 0003.
    """

    dependencies = [
        ('payroll', '0001_initial'),
    ]

    operations = [
        # No-op: columns were added in a previous deployment
        # Safe version is in 0003
    ]
