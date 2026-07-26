from django.db import migrations, models


def backfill_topic_keys(apps, schema_editor):
    from content_pipeline.instagram import normalize_topic_key

    InstagramCarousel = apps.get_model('content_pipeline', 'InstagramCarousel')
    for carousel in InstagramCarousel.objects.all().iterator():
        key = normalize_topic_key(topic=carousel.topic or '', title=carousel.title or '')
        if key:
            carousel.topic_key = key
            carousel.save(update_fields=['topic_key'])


class Migration(migrations.Migration):

    dependencies = [
        ('content_pipeline', '0003_instagram_title_optional'),
    ]

    operations = [
        migrations.AddField(
            model_name='instagramcarousel',
            name='topic_key',
            field=models.CharField(blank=True, db_index=True, editable=False, help_text='Assunto normalizado — evita duplicatas.', max_length=255),
        ),
        migrations.AddField(
            model_name='instagramcarousel',
            name='export_paths',
            field=models.JSONField(blank=True, default=list, help_text='Paths relativos em media/ (ex.: instagram/2/slide-01.png).'),
        ),
        migrations.AddField(
            model_name='instagramcarousel',
            name='exported_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RunPython(backfill_topic_keys, migrations.RunPython.noop),
    ]
