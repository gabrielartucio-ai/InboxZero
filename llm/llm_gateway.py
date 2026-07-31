from langchain.chat_models import init_chat_model
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_not_exception_type
from pydantic import BaseModel, ValidationError
from typing import Type, TypeVar, Any
from config.config_app import ConfigApp

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

TBaseModel = TypeVar("TBaseModel", bound=BaseModel)

class LLMGateway:
    """
    Encapsula el acceso a modelos de lenguaje (LLM) mediante LangChain.

    Esta clase inicializa el modelo configurado en la aplicación y
    proporciona métodos para realizar solicitudes al LLM, incluyendo
    la generación de respuestas estructuradas validadas mediante
    esquemas Pydantic.
    """
    
    def __init__(self, agent_id: str | None = None):
        self.llm_profile = self._resolve_model_profile(agent_id=agent_id)
        self._base_model = init_chat_model(
            model = self.llm_profile["model"],
            model_provider = self.llm_profile["provider"],
            temperature = self.llm_profile["temperature"]
        )

    def _resolve_model_profile(self, agent_id: str | None)  -> dict[str, Any]:
        default_profile_name = self.config.llm_profiles["default_profile"]
        default_profile = self.config.llm_profiles["profiles"][default_profile_name]
        if not agent_id:
            selected_profile = default_profile
        else:
            try:
                profile_name = self.config.llm_profiles["agent_profiles"][agent_id]["profile"]
                selected_profile = self.config.llm_profiles["profiles"][profile_name]
            except KeyError as e:
                logger.error(f"Agente o perfil desconocido: {e}. Se usará el LLM por defecto")
                selected_profile = default_profile
        return {"provider": selected_profile["provider"],
                "model": selected_profile["model"],
                "temperature": selected_profile["temperature"]}
    
    def request_structured_output(self,
                                system_prompt: str, 
                                input_text: str,
                                output_schema: Type[TBaseModel]) -> TBaseModel:
        structured_model = self._base_model.with_structured_output(output_schema)
        message = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": input_text}
        ]
        try:
            result = self.llm_calling(structured_model, message)
        except ValidationError as e:
            logger.error(f"Fallo de validación de schema en respuesta LLM: {e}")
            raise 
        except Exception as e:
            logger.error(f"Error al invocar el modelo LLM ({type(e).__name__}): {e}")
            raise
        else:
            return result

    @staticmethod
    def log_retry_attempt(retry_state):
            """Aviso que se imprime en consola antes de cada reintento."""
            tried = retry_state.attempt_number
            print(f"⚠️ [AVISO] Problema de conexión al LLM. Reintentando en breve... (Intento {tried})")

    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=log_retry_attempt,
        retry=retry_if_not_exception_type(ValidationError), 
        reraise=True 
    )
    def llm_calling(self, 
                    structured_model,
                    message: list[dict]) -> TBaseModel:
        model_result = structured_model.invoke(message)
        return model_result 

