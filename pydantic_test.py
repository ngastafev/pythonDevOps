from pydantic import BaseModel, field_validator, Field
from typing import List


class Service(BaseModel):
    name: str
    replicas: int = Field(ge=0, default=1)
    containers: List[str] = Field(default_factory=list)

    @field_validator('containers', mode='before')
    @classmethod
    def parse_containers(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(',') if item.strip()]
        return v

    @field_validator('containers')
    @classmethod
    def validate_containers(cls, v):
        if not all(v):
            raise ValueError('Container names cannot be empty')
        return v

service_x = Service(name="Test1", containers="A,B")
print(service_x.containers)

try:
    Service(name="test", containers=["", "web"])
except ValueError as e:
    print(e)