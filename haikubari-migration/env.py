from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app.core.settings import settings
from app.model.base import Base

# WAJIB import semua model supaya autogenerate kebaca
from app.model.user import User
from app.model.haiku import Haiku
from app.model.like import Like
from app.model.otp import OTP
from app.model.review import Review
# from app.modls.review import Review  # kalau ada

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Alembic butuh SYNC driver
DB_URL = str(settings.DATABASE_URL).replace("+asyncpg", "+psycopg2")


def run_migrations_offline() -> None:
    context.configure(
        url=DB_URL,                      # <- langsung, gak lewat config parser
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        DB_URL,                          # <- langsung juga
        poolclass=pool.NullPool,
        future=True,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()