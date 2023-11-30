from sqlalchemy import MetaData
from sqlalchemy.orm import registry

mapper_registry = registry(metadata=MetaData(schema='public'))
metadata = mapper_registry.metadata
