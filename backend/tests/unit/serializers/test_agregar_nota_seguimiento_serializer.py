"""
Tests unitarios - AgregarNotaSeguimientoInputSerializer
HU Consultor: Agregar nota de seguimiento (10-1000 caracteres)
"""
import pytest
from atenciones.serializers.input.agregar_nota_seguimiento_input_serializer import (
    AgregarNotaSeguimientoInputSerializer,
)


def _valid(data):
    s = AgregarNotaSeguimientoInputSerializer(data=data)
    assert s.is_valid(), s.errors
    return s.validated_data


def _invalid(data):
    s = AgregarNotaSeguimientoInputSerializer(data=data)
    assert not s.is_valid()
    return s.errors


# Casos válidos

def test_contenido_exactamente_10_caracteres_es_valido():
    data = _valid({"contenido": "1234567890"})
    assert data["contenido"] == "1234567890"


def test_contenido_exactamente_1000_caracteres_es_valido():
    data = _valid({"contenido": "a" * 1000})
    assert len(data["contenido"]) == 1000


def test_contenido_normal_es_valido():
    data = _valid({"contenido": "Nota de seguimiento con información relevante."})
    assert "Nota de seguimiento" in data["contenido"]


def test_campo_opcional_sin_enviar_es_valido():
    data = _valid({})
    assert data.get("contenido", "") == ""


def test_contenido_vacio_string_es_valido():
    """Si viene vacío el serializer lo acepta; la view decide no guardar."""
    data = _valid({"contenido": ""})
    assert data["contenido"] == ""


def test_contenido_con_espacios_extra_se_hace_strip():
    data = _valid({"contenido": "  Nota con espacios al inicio y al final.  "})
    assert not data["contenido"].startswith(" ")
    assert not data["contenido"].endswith(" ")


# Casos inválidos

def test_contenido_menor_a_10_caracteres_es_invalido():
    errors = _invalid({"contenido": "corta"})
    assert "contenido" in errors


def test_contenido_9_caracteres_es_invalido():
    errors = _invalid({"contenido": "123456789"})
    assert "contenido" in errors


def test_contenido_1001_caracteres_es_invalido():
    errors = _invalid({"contenido": "x" * 1001})
    assert "contenido" in errors


def test_mensaje_error_es_correcto():
    s = AgregarNotaSeguimientoInputSerializer(data={"contenido": "abc"})
    s.is_valid()
    messages = [str(e) for e in s.errors.get("contenido", [])]
    assert any("10" in m and "1000" in m for m in messages)


def test_solo_espacios_no_supera_minimo():
    """Espacios en blanco no deben contar como contenido válido."""
    s = AgregarNotaSeguimientoInputSerializer(data={"contenido": "          "})
    s.is_valid()
    assert s.validated_data.get("contenido", "") == ""