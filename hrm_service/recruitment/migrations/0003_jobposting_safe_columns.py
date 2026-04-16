from django.db import migrations


class Migration(migrations.Migration):
    """No-op: already applied on prod DB from prior deployment."""

    dependencies = [
        ('recruitment', '0002_add_draft_posted_status_to_jobposting'),
    ]

    operations = []
