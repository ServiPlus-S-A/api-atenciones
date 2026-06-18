from django.core.cache import cache


class AtencionCacheService:
    """Servicio de caché para el módulo de Atenciones.

    Maneja la invalidación selectiva de listados cacheados.
    """

    @staticmethod
    def invalidate_after_create(
        created_by: str | None, consultor_ids: list[str]
    ) -> None:
        """Invalida las claves de listado afectadas por la creación de una atención."""
        keys_to_delete = []

        # Claves legacy: listado_ROL_USERID
        # Invalidamos para el creador y para cada consultor asignado
        roles = [
            "Coordinador",
            "Consultor",
            "Cliente",
            "COORDINADOR",
            "CONSULTOR",
            "CLIENTE",
        ]

        users_to_invalidate = []
        if created_by:
            users_to_invalidate.append(str(created_by))
        for cid in consultor_ids:
            users_to_invalidate.append(str(cid))

        for uid in users_to_invalidate:
            for rol in roles:
                keys_to_delete.append(f"listado_{rol}_{uid}")

        # Claves basadas en patrones estructurados
        # Para LocMemCache/Memcached que no soportan wildcard keys de forma nativa,
        # eliminamos las claves directas si se conocen, y agregamos patrones.
        for uid in users_to_invalidate:
            keys_to_delete.append(f"atenciones:user:{uid}:list")
            keys_to_delete.append(f"atenciones:consultor:{uid}:list")

        keys_to_delete.append("atenciones:list:all")

        # Eliminar todas las claves acumuladas
        cache.delete_many(keys_to_delete)
