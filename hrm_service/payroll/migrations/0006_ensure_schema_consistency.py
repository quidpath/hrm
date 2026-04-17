# Generated migration to ensure schema consistency
from django.db import migrations


class Migration(migrations.Migration):
    """
    This migration ensures the database schema matches the model definition
    without attempting to add columns that already exist.
    """

    dependencies = [
        ('payroll', '0005_payrollrun_safe_columns'),
    ]

    operations = [
        # Use raw SQL to safely ensure all columns exist without conflicts
        migrations.RunSQL(
            sql=[
                # Ensure all PayrollRun columns exist (using IF NOT EXISTS to avoid conflicts)
                "ALTER TABLE payroll_payrollrun ADD COLUMN IF NOT EXISTS drafted_at TIMESTAMP WITH TIME ZONE NULL;",
                "ALTER TABLE payroll_payrollrun ADD COLUMN IF NOT EXISTS posted_at TIMESTAMP WITH TIME ZONE NULL;",
                "ALTER TABLE payroll_payrollrun ADD COLUMN IF NOT EXISTS posted_by UUID NULL;",
                
                # Ensure indexes exist
                "CREATE INDEX IF NOT EXISTS payroll_payrollrun_state_idx ON payroll_payrollrun (state);",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]