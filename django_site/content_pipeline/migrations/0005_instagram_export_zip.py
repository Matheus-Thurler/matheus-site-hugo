from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content_pipeline', '0004_instagram_export_and_topic_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='instagramcarousel',
            name='export_zip_path',
            field=models.CharField(
                blank=True,
                help_text='Path relativo do ZIP em media/ (ex.: instagram/2/carousel-2.zip).',
                max_length=500,
            ),
        ),
    ]
