import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Atencion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("estado", models.CharField(default="AGENDADA", max_length=20)),
                ("solicitud_id", models.IntegerField(db_index=True)),
                ("fecha_programada", models.DateTimeField(blank=True, null=True)),
                ("fecha_fin", models.DateTimeField(blank=True, null=True)),
                ("notas_finales", models.TextField(blank=True, null=True)),
                ("fecha_cierre", models.DateTimeField(blank=True, null=True)),
                ("creado_por_id", models.IntegerField()),
                ("motivo_anulacion", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"db_table": "atencion"},
        ),
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("operacion", models.CharField(max_length=64)),
                ("actor_id", models.IntegerField()),
                ("actor_rol", models.CharField(max_length=32)),
                ("atencion_id", models.IntegerField(blank=True, null=True)),
                ("payload_hash_sha256", models.CharField(max_length=64)),
                ("jwt_subject", models.CharField(max_length=255)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
            ],
            options={"db_table": "audit_log"},
        ),
        migrations.CreateModel(
            name="AtencionConsultor",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("consultor_id", models.IntegerField()),
                ("es_lider", models.BooleanField(default=False)),
                (
                    "atencion",
                    models.ForeignKey(
                        db_column="atencion_fk",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="consultores_rel",
                        to="atenciones.atencion",
                    ),
                ),
            ],
            options={"db_table": "atencion_consultor"},
        ),
        migrations.CreateModel(
            name="NotaSeguimiento",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("consultor_id", models.IntegerField()),
                ("contenido", models.TextField()),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "atencion",
                    models.ForeignKey(
                        db_column="atencion_fk",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notas",
                        to="atenciones.atencion",
                    ),
                ),
            ],
            options={"db_table": "nota_seguimiento", "ordering": ["-timestamp"]},
        ),
        migrations.AddIndex(
            model_name="atencion",
            index=models.Index(fields=["estado", "fecha_programada"], name="atencion_estado_fecha_idx"),
        ),
        migrations.AddIndex(
            model_name="auditlog",
            index=models.Index(fields=["timestamp"], name="audit_log_timestamp_idx"),
        ),
        migrations.AlterUniqueTogether(
            name="atencionconsultor",
            unique_together={("atencion", "consultor_id")},
        ),
    ]
