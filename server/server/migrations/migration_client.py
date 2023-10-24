from pathlib import Path

from yoyo import get_backend, read_migrations

MIGRATIONS_FOLDER_PATH = Path(__file__).parent / "migration_steps"


class MigrationClient:
    def __init__(self, db_connection_str: str):
        self._backend = get_backend(db_connection_str)
        self._migrations = read_migrations(str(MIGRATIONS_FOLDER_PATH))

    def run_migrations(self):
        with self._backend.lock():
            self._backend.apply_migrations(self._backend.to_apply(self._migrations))
