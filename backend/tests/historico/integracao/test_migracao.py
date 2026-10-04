from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, inspect


def test_migracao_do_historico_e_reversivel(
    motor_de_teste: Engine, configuracao_do_alembic: Config
) -> None:
    command.downgrade(configuracao_do_alembic, "base")
    assert "registro_de_historico" not in inspect(motor_de_teste).get_table_names()

    command.upgrade(configuracao_do_alembic, "head")
    assert "registro_de_historico" in inspect(motor_de_teste).get_table_names()
