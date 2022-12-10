import sqlalchemy


metadata = sqlalchemy.MetaData()
worker = sqlalchemy.Table(
    "worker",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("ip", sqlalchemy.String(45), index=True, unique=False, nullable=False),
    sqlalchemy.Column("address", sqlalchemy.Text, index=True, unique=False, nullable=False),
    sqlalchemy.Column("hardware", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("hardware_id", sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column("caption", sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column("connected_at", sqlalchemy.DateTime(timezone=False), nullable=False),
    sqlalchemy.Column("disconnected_at", sqlalchemy.DateTime(timezone=False), nullable=True),
    sqlalchemy.Index("worker_hardware_id_caption", "hardware_id", "caption"),
)
