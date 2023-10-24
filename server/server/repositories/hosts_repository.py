from abc import ABC
from sqlite3 import Cursor

from pydantic import UUID4

from domain.host import Host


class HostsRepository(ABC):
    """Repository to handle CRUD operations on hosts"""
    # TODO abstract methods


class SQLiteHostsRepository(HostsRepository):
    def __init__(self, sqlite_cursor: Cursor):
        self._sqlite_cursor = sqlite_cursor

    def get_all(self) -> list[Host]:
        """Get all hosts."""
        # TODO pagination
        hosts_res = self._sqlite_cursor.execute(
            """
            SELECT id, label, last_known_host, last_seen, os, memory, cpu_cores
            FROM hosts
            """
        )
        hosts = []
        for res_tuple in hosts_res.fetchall():
            pass
            # TODO map results to host
        # TODO fetch applications for each host
        return hosts

    def get_host(self, host_id: UUID4) -> Host | None:
        """Get a host by id."""
        host_res = self._sqlite_cursor.execute(
            """
            SELECT id, label, last_known_host, last_seen, os, memory, cpu_cores
            FROM hosts
            WHERE id = ?
            """,
            (str(host_id),)
        )
        host_res.fetchone()
        # TODO fetch applications for host
        return None

    def create_host(self, host: Host):
        """Create a host."""
        create_res = self._sqlite_cursor.execute(
            """
            INSERT INTO hosts(id, label, last_known_host, last_seen, os, memory, cpu_cores)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                host.id,
                host.label,
                host.last_known_host,
                host.last_seen,
                host.attributes.os,
                host.attributes.memory,
                host.attributes.cpu_cores
            )
        )

    def update_host(self, host: Host):
        """Update a host."""

    def delete_host(self, host_id: UUID4):
        """Delete a host."""
