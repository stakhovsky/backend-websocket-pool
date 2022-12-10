import sqlalchemy


metadata = sqlalchemy.MetaData()
job = sqlalchemy.Table(
    "job",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("block_height", sqlalchemy.Integer, index=True, unique=True, nullable=False),
    sqlalchemy.Column("epoch_challenge", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("task_id", sqlalchemy.String(36), index=True, unique=True, nullable=False),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime(timezone=False), nullable=False, server_default=sqlalchemy.text("(now() at time zone 'utc')")),
)
