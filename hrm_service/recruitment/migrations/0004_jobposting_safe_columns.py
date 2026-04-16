from django.db import migrations


class Migration(migrations.Migration):
    """
    Safely ensures drafted_at, posted_at, posted_by exist on recruitment_jobposting.
    Uses IF NOT EXISTS — safe on both fresh and existing prod DBs.
    """

    dependencies = [
        ('recruitment', '0003_jobposting_safe_columns'),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                "ALTER TABLE recruitment_jobposting ADD COLUMN IF NOT EXISTS drafted_at TIMESTAMP WITH TIME ZONE NULL;",
                "ALTER TABLE recruitment_jobposting ADD COLUMN IF NOT EXISTS posted_at TIMESTAMP WITH TIME ZONE NULL;",
                "ALTER TABLE recruitment_jobposting ADD COLUMN IF NOT EXISTS posted_by UUID NULL;",
            ],
            reverse_sql=[
                "ALTER TABLE recruitment_jobposting DROP COLUMN IF EXISTS drafted_at;",
                "ALTER TABLE recruitment_jobposting DROP COLUMN IF EXISTS posted_at;",
                "ALTER TABLE recruitment_jobposting DROP COLUMN IF EXISTS posted_by;",
            ],
        ),
        migrations.RunSQL(
            sql="CREATE INDEX IF NOT EXISTS jobposting_state_idx ON recruitment_jobposting (state);",
            reverse_sql="DROP INDEX IF EXISTS jobposting_state_idx;",
        ),
    ]
