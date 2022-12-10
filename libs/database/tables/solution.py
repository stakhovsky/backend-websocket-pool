import sqlalchemy


metadata = sqlalchemy.MetaData()
solution = sqlalchemy.Table(
    "solution",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("hardware_id", sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column("caption", sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column("task_id", sqlalchemy.String(36), index=True, unique=False, nullable=False),
    sqlalchemy.Column("unique_key", sqlalchemy.Text, unique=True, nullable=False),
    sqlalchemy.Column("solution", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("valid", sqlalchemy.Boolean, server_default=sqlalchemy.text("false"), nullable=False),
    sqlalchemy.Column("checked", sqlalchemy.Boolean, server_default=sqlalchemy.text("false"), nullable=False),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime(timezone=False), nullable=False, server_default=sqlalchemy.text("(now() at time zone 'utc')")),
    sqlalchemy.Index("solution_hardware_id_caption", "hardware_id", "caption"),
)
