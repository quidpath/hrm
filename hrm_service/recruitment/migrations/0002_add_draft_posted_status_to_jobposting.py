# Generated migration for adding draft/posted timestamps to JobPosting

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobposting',
            name='drafted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='jobposting',
            name='posted_at',
            field=models.DateTimeField(blank=True, null=True, help_text='When job was published/opened'),
        ),
        migrations.AddField(
            model_name='jobposting',
            name='posted_by',
            field=models.UUIDField(blank=True, null=True, help_text='User ID who posted the job'),
        ),
        migrations.AddIndex(
            model_name='jobposting',
            index=models.Index(fields=['state'], name='jobposting_state_idx'),
        ),
    ]
