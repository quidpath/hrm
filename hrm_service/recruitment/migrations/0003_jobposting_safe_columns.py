from django.db import migrations


class Migration(migrations.Migration):
    """
    Safely ensures drafted_at, posted_at, posted_by columns exist on recruitment_jobposting.
    Uses IF NOT EXISTS so it works on both fresh DBs and existing ones.
    """

    dependencies = [
        ('recruitment', '0002_add_draft_posted_status_to_jobposting'),
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
