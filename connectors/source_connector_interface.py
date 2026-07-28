from abc import ABC, abstractmethod
from config.config_app import ConfigApp
from schemas.schemas_and_state import RawMail

class SourceConnectorInterface(ABC):

    def __init__(self, config: ConfigApp):
        self.config = config
        self.connected = False

    @abstractmethod
    def connect(self) -> None:
        ...

    @abstractmethod    
    def get_recent_emails(self, cantidad: int) -> list[RawMail]:
        ...
   
    def _validate_limit(self, cantidad: int) -> None:
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero")
