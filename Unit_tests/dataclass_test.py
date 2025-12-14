
import pytest
from dataclasses import dataclass, field

@dataclass
class Service:
    name: str
    replicas: int = 1
    containers: list[str] = field(default_factory=list)

    def scale(self, delta: int) -> None:
        self.replicas = max(0, self.replicas + delta)

def test_scale_up():
    # ARRANGE
    service = Service("Test", replicas=2)
    expected_replicas = 5

    # ACT
    service.scale(3)

    # ASSERT
    assert service.replicas == expected_replicas

def test_scale_down():
    # ARRANGE
    service = Service("Test", replicas=3)
    expected_replicas = 2

    # ACT
    service.scale(-1)

    # ASSERT
    assert service.replicas == expected_replicas

def test_scale_down_below_zero():
    # ARRANGE
    service = Service("Test", replicas=2)
    expected_replicas = 0

    # ACT
    service.scale(-5)

    # ASSERT
    assert service.replicas == expected_replicas

def test_scale_no_change():
    # ARRANGE
    service = Service("Test", replicas=4)
    expected_replicas = 4

    # ACT
    service.scale(0)

    # ASSERT
    assert service.replicas == expected_replicas

def test_default_replicas():
    # ARRANGE
    service = Service("Test")

    # ASSERT
    assert service.replicas == 1

def test_default_containers():
    # ARRANGE
    service = Service("Test")

    # ASSERT
    assert service.containers == []