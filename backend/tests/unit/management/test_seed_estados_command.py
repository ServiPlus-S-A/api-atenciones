import io

import pytest
from django.core.management import call_command


@pytest.mark.unit
def test_seed_estados_command_outputs_states():
    out = io.StringIO()

    call_command("seed_estados", stdout=out)

    output = out.getvalue()
    assert "Estado disponible:" in output
    assert "Estados de atención verificados" in output
