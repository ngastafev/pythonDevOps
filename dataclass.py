from dataclasses import dataclass, field

@dataclass
class Service:
    name : str
    replicas : int = 1
    containers : list[str] = field(default_factory=list)

    def scale (self, delta : int) -> None:
        self.replicas = max(0,self.replicas + delta)
service_x = Service ("Test1", 3, ["A", "B", "C"])
#Должен вернуть 2
service_x.scale(-1)
print(service_x.replicas)
#Должен вернуть 0
service_x.scale(-5)
print(service_x.replicas)
service_e=("Test", 2, "string")
service_e.scale(-1)
print(service_e.replicas)