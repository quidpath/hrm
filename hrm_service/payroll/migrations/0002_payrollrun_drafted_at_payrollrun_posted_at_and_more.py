from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Safe migration using IF NOT EXISTS to handle cases where columns
    were already added directly to the database.
    """

    dependencies = [
        ('payroll', '0001_initial'),
    ]

    operations = [
        # Use RunSQL with IF NOT EXISTS to safely add columns that may already exist
        migrations.RunSQL(
            sql=[
                "ALTER TABLE payroll_payrollrun ADD COLUMN IF NOT EXISTS drafted_at TIMESTAMP WITH TIME ZONE NULL;",
                "ALTER TABLE payroll_payrollrun ADD COLUMN IF NOT EXISTS posted_at TIMESTAMP WITH TIME ZONE NULL;",
                "ALTER TABLE payroll_payrollrun ADD COLUMN IF NOT EXISTS posted_by UUID NULL;",
                "ALTER TABLE payroll_payrollrun ADD COLUMN IF NOT EXISTS state VARCHAR(20) NOT NULL DEFAULT 'draft';" if False else "SELECT 1;",
            ],
            reverse_sql=[
                "ALTER TABLE payroll_payrollrun DROP COLUMN IF EXISTS drafted_at;",
                "ALTER TABLE payroll_payrollrun DROP COLUMN IF EXISTS posted_at;",
                "ALTER TABLE payroll_payrollrun DROP COLUMN IF EXISTS posted_by;",
            ],
        ),
        # Update the state field to add db_index (safe - just adds index)
        migrations.RunSQL(
            sql="CREATE INDEX IF NOT EXISTS payroll_payrollrun_state_idx ON payroll_payrollrun (state);",
            reverse_sql="DROP INDEX IF EXISTS payroll_payrollrun_state_idx;",
        ),
    ]
