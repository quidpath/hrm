# Generated migration for adding draft/posted timestamps to PayrollRun

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='payrollrun',
            name='drafted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='payrollrun',
            name='posted_at',
            field=models.DateTimeField(blank=True, null=True, help_text='When payroll was approved/posted'),
        ),
        migrations.AddField(
            model_name='payrollrun',
            name='posted_by',
            field=models.UUIDField(blank=True, null=True, help_text='User ID who posted/approved the payroll'),
        ),
        migrations.AddIndex(
            model_name='payrollrun',
            index=models.Index(fields=['state'], name='payroll_state_idx'),
        ),
    ]
