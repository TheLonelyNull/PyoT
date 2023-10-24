from yoyo import step

steps = [
    step(
        """
        CREATE TABLE hosts (
            id VARCHAR(36),
            label VARCHAR(255),
            last_known_host VARCHAR(50),
            last_seen TIMESTAMP,
            os VARCHAR(255),
            memory INT,
            cpu_cores INT,
            PRIMARY KEY (id)
        )
        """,
        """
        DROP TABLE hosts
        """
    )
]