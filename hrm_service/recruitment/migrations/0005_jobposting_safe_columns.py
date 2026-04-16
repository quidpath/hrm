from django.db import migrations


class Migration(migrations.Migration):
    """Safely adds recruitment columns using IF NOT EXISTS."""

    dependencies = [
        ('recruitment', '0004_jobposting_safe_columns'),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                "ALTER TABLE recruitment_jobposting ADD COLUMN IF NOT EXISTS drafted_at TIMESTAMP WITH TIME ZONE NULL;",
                "ALTER TABLE recruitment_jobposting ADD COLUMN IF NOT EXISTS posted_at TIMESTAMP WITH TIME ZONE NULL;",
                "ALTER TABLE recruitment_jobposting ADD COLUMN IF NOT EXISTS posted_by UUID NULL;",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="CREATE INDEX IF NOT EXISTS jobposting_state_idx ON recruitment_jobposting (state);",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
