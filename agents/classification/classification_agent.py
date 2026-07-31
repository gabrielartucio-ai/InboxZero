from llm.llm_gateway import LLMGateway
from schemas.schemas_and_state import CleanMail, MailClassification
from agents.classification.prompts import build_classification_system_prompt

AGENT_ID = "classification_agent" 

class ClassificationAgent:
    def __init__(self):
        self.llm_gateway = LLMGateway(agent_id=AGENT_ID)
        self.system_prompt = self._build_system_prompt()
        self.system_prompt = build_classification_system_prompt()

    def email_classificator(self, clean_mail: CleanMail) -> MailClassification:
        model_response = self.llm_gateway.request_structured_output(
            system_prompt=self.system_prompt, 
            input_text=clean_mail.body_clean, 
            output_schema=MailClassification
            )
        return model_response

    def _build_input_text(clean_mail: CleanMail) -> str:
        subject = clean_mail.subject
        sender_name = clean_mail.sender_name
        sent_at = clean_mail.sent_at
        language = clean_mail.language
        body = clean_mail.body_clean
        texto =(f"Asunto: {subject}.\nRemitente: {sender_name}.\n"
                f"Fecha de envío:{sent_at}.\nIdioma: {language}.\n"
                f"Cuerpo principal de correo: {body}.") 
        print(texto)
        return texto



    

