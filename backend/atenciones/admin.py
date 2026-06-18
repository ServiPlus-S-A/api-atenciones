from django.contrib import admin
from atenciones.models import Atention, AtentionConsultant, MonitoringNote, AuditLog


@admin.register(Atention)
class AtentionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "request_id",
        "status",
        "scheduled_date",
        "closing_date",
        "created_by",
        "created_at",
    )
    list_filter = ("status", "scheduled_date")
    search_fields = ("request_id", "final_note")
    ordering = ("-created_at",)


@admin.register(AtentionConsultant)
class AtentionConsultantAdmin(admin.ModelAdmin):
    list_display = ("id", "atention", "consultant_id", "is_leader")
    list_filter = ("is_leader",)
    search_fields = ("consultant_id", "atention__id")


@admin.register(MonitoringNote)
class MonitoringNoteAdmin(admin.ModelAdmin):
    list_display = ("id", "atention", "consultant_id", "created_at")
    search_fields = ("content", "consultant_id")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "operation",
        "actor_id",
        "actor_role",
        "atention_id",
        "created_at",
    )
    readonly_fields = (
        "operation",
        "actor_id",
        "actor_role",
        "atention_id",
        "payload_hash_sha256",
        "jwt_subject",
        "created_at",
    )
    list_filter = ("operation", "actor_role", "created_at")
