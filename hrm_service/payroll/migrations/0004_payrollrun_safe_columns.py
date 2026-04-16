from django.db import migrations


class Migration(migrations.Migration):
    """
    Safely ensures drafted_at, posted_at, posted_by exist on payroll_payrollrun.
    Uses IF NOT EXISTS — safe on both fresh and existing prod DBs.
    """

    dependencies = [
        ('payroll', '0003_payrollrun_safe_columns'),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                "ALTER TABLE payroll_payrollrun ADD COLUMN IF NOT EXISTS drafted_at TIMESTAMP WITH TIME ZONE NULL;",
                "ALTER TABLE payroll_payrollrun ADD COLUMN IF NOT EXISTS posted_at TIMESTAMP WITH TIME ZONE NULL;",
                "ALTER TABLE payroll_payrollrun ADD COLUMN IF NOT EXISTS posted_by UUID NULL;",
            ],
            reverse_sql=[
                "ALTER TABLE payroll_payrollrun DROP COLUMN IF EXISTS drafted_at;",
                "ALTER TABLE payroll_payrollrun DROP COLUMN IF EXISTS posted_at;",
                "ALTER TABLE payroll_payrollrun DROP COLUMN IF EXISTS posted_by;",
            ],
        ),
        migrations.RunSQL(
            sql="CREATE INDEX IF NOT EXISTS payroll_payrollrun_state_idx ON payroll_payrollrun (state);",
            reverse_sql="DROP INDEX IF EXISTS payroll_payrollrun_state_idx;",
        ),
    ]
