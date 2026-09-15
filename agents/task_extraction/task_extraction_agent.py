from config.config_app import ConfigApp
from llm.llm_gateway import LLMGateway
from schemas.schemas_and_state import CleanMail, TaskExtraction
from agents.classification.prompts import build_extractor_system_prompt

AGENT_ID = "task_extraction_agent" 

class TaskExtractionAgent:
    def __init__(self, config: ConfigApp):
        self.llm_gateway = LLMGateway(config=config, agent_id=AGENT_ID)
        self.system_prompt = build_extractor_system_prompt()

    def email_extractor(self, clean_mail: CleanMail) -> TaskExtraction:
        model_response = self.llm_gateway.request_structured_output(
            system_prompt=self.system_prompt, 
            input_text=self._build_input_text(clean_mail), 
            output_schema=TaskExtraction
            )
        print(f"has_tasks: {model_response.has_task}")
        for elem in model_response.tasks:
            print(f"task_id: {elem.task_id}")
            print(f"task_title: {elem.task_title}")
            print(f"task_description: {elem.task_description}")

        print(f"assigned_to: {model_response.task_assigned_to}")
        return model_response


    @staticmethod
    def _build_input_text(clean_mail: CleanMail) -> str:
        subject = clean_mail.subject
        sender_name = clean_mail.sender_name
        sent_at = clean_mail.sent_at
        language = clean_mail.language
        body = clean_mail.body_clean
        texto =(f"Asunto: {subject}.\nRemitente: {sender_name}.\n"
                f"Fecha de envío:{sent_at}.\nIdioma: {language}.\n"
                f"Cuerpo principal de correo: {body}.") 
        return texto
