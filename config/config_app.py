import os
import logging
import json
from dotenv import load_dotenv
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigApp:
    """
    Centraliza la configuración global de la aplicación.

    Este componente es responsable de:

    - Cargar las variables de entorno desde el archivo .env.
    - Inicializar los parámetros generales de configuración.
    - Construir las credenciales necesarias para Exchange.
    - Cargar el archivo llm_profiles.json con la configuración de los
      modelos de lenguaje.
    - Validar que la configuración mínima requerida exista antes de que
      la aplicación continúe su ejecución.

    No establece conexiones con servicios externos ni realiza ninguna
    lógica de negocio. Su única responsabilidad es proporcionar una
    configuración consistente al resto de los componentes.
    """

    TIMEZONE: str = "America/Montevideo"
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    json_file = PROJECT_ROOT / "llm" / "llm_profiles.json"

    def __init__(self, password: str) -> None:
        """
        Inicializa la configuración de la aplicación.

        Carga las variables de entorno, construye las credenciales del
        usuario, valida la configuración general y carga la configuración
        de los modelos de lenguaje desde el archivo llm_profiles.json.
        """
        load_dotenv()
        self.GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
        self.SUPABASE_URL: str | None = os.getenv("SUPABASE_URL")
 
        self.MAIL_SERVER_URL: str | None = os.getenv("MAIL_SERVER_URL")
        self.EMAIL_ADDRESS: str | None = os.getenv("EMAIL_ADDRESS")
        self.USER_DOMAIN: str | None = os.getenv("USER_DOMAIN")
        self.USER: str | None = os.getenv("USER")
        self.USERNAME: str = f"{self.USER_DOMAIN}\\{self.USER}"
        self.PASSWORD: str | None = password
        # Verifica que toda la configuración crítica esté disponible antes de
        # continuar con la inicialización de la aplicación.
        self._validate_environment_config()
        # Carga la configuración de los perfiles LLM.
        # El archivo se encuentra dentro de la carpeta config.
        json_file = self.PROJECT_ROOT / "llm" / "llm_profiles.json"
        with json_file.open("r", encoding="utf-8") as file:
            self.llm_profiles = json.load(file)
        self._validate_llm_profiles_file()

    def _validate_environment_config(self) -> None:
        """Verifica que las variables críticas existan al arrancar."""
        invalid_values = (None, "")
        missing = [k for k, v in self.__dict__.items() if v in invalid_values]
        if missing:
            raise ValueError(f"Faltan variables de entorno críticas: {', '.join(missing)}")      
        
    def _validate_llm_profiles_file(self) -> None:
        """
        Verifica que la configuración cargada desde llm_profiles.json
        sea un objeto JSON representado como un diccionario Python.
        """
        if  not isinstance(self.llm_profiles, dict):
            logger.error("Error en el archivo JSON: llm_profiles no es un diccionario")
            raise TypeError("Error en el archivo JSON: llm_profiles no es un diccionario")


