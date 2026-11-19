from django.db import migrations, models

import core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_delete_imagemodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=core.models.avatar_upload_to,
                verbose_name='Аватар',
            ),
        ),
    ]
