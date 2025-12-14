
import pytest
from pydantic import ValidationError
from typing import List
from pydantic import BaseModel, field_validator, Field

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

def test_default_replicas():
    service = Service(name="Test")
    assert service.replicas == 1

def test_replicas_ge_zero():
    with pytest.raises(ValidationError):
        Service(name="Test", replicas=-1)

def test_string_containers_parsing():
    service = Service(name="Test", containers="A, B, C")
    assert service.containers == ["A", "B", "C"]

def test_list_containers():
    service = Service(name="Test", containers=["A", "B"])
    assert service.containers == ["A", "B"]

def test_empty_container_name_validation():
    with pytest.raises(ValidationError, match="Container names cannot be empty"):
        Service(name="Test", containers=["", "B"])

def test_empty_string_in_parsed_list():
    with pytest.raises(ValidationError, match="Container names cannot be empty"):
        Service(name="Test", containers="A,,B")