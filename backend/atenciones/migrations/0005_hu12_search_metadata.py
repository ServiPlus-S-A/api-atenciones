from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("atenciones", "0004_unique_leader_per_atention"),
    ]

    operations = [
        migrations.AddField(
            model_name="atention",
            name="customer_name",
            field=models.CharField(
                blank=True, db_index=True, max_length=255, null=True
            ),
        ),
        migrations.AddField(
            model_name="atentionconsultant",
            name="consultant_name",
            field=models.CharField(
                blank=True, db_index=True, max_length=255, null=True
            ),
        ),
    ]
