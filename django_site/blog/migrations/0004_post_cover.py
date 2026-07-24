from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='cover',
            field=models.CharField(
                blank=True,
                help_text='Cover image path (/images/covers/...) or external URL',
                max_length=500,
            ),
        ),
    ]
