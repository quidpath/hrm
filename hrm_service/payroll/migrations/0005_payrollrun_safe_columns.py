from django.db import migrations


class Migration(migrations.Migration):
    """Safely adds payroll columns using IF NOT EXISTS."""

    dependencies = [
        ('payroll', '0004_payrollrun_safe_columns'),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                "ALTER TABLE payroll_payrollrun ADD COLUMN IF NOT EXISTS drafted_at TIMESTAMP WITH TIME ZONE NULL;",
                "ALTER TABLE payroll_payrollrun ADD COLUMN IF NOT EXISTS posted_at TIMESTAMP WITH TIME ZONE NULL;",
                "ALTER TABLE payroll_payrollrun ADD COLUMN IF NOT EXISTS posted_by UUID NULL;",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="CREATE INDEX IF NOT EXISTS payroll_payrollrun_state_idx ON payroll_payrollrun (state);",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
