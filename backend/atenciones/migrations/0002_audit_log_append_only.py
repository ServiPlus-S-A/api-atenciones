# CONCERN-04: revoca UPDATE/DELETE sobre audit_log al rol de la app
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("atenciones", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            REVOKE UPDATE, DELETE ON audit_log FROM PUBLIC;
            """,
            reverse_sql="""
            GRANT UPDATE, DELETE ON audit_log TO PUBLIC;
            """,
        ),
    ]
