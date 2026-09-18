from config.config_app import ConfigApp
from llm.llm_gateway import LLMGateway
from schemas.schemas_and_state import CleanMail, SecurityAnalysis
from agents.security_analysis.prompts import build_security_system_prompt

AGENT_ID = "security_analysis_agent" 

class SecurityAnalysisAgent:
    def __init__(self, config: ConfigApp):
        self.llm_gateway = LLMGateway(config=config, agent_id=AGENT_ID)
        self.system_prompt = build_security_analysis_system_prompt()

    def email_security_analyzer(self, clean_mail: CleanMail) -> SecurityAnalysis
        model_response = self.llm_gateway.request_structured_output(
            system_prompt=self.system_prompt, 
            input_text=self._build_input_text(clean_mail), 
            output_schema=SecurityAnalysis
            )
        print(f"is_suspicious: {model_response.is_suspicious}")
        print(f"risk_level: {model_response.risk_level}")
        for elem in model_response.threat_types:
            print(f"threat_type: {elem}")
        for elem in model_response.suspicious_links:
            print(f"suspicious_link: {elem}")
        for elem in model_response.suspicious_indicators:
            print(f"suspicious_indicator: {elem}")
        print(f"razonamiento: {model_response.reasoning}")
        return model_response

    @staticmethod
    def _build_input_text(clean_mail: CleanMail) -> str:
        subject = clean_mail.subject
        sender_name = clean_mail.sender_name
        sender_address = clean_mail.sender_address
        reply_to_address = clean_mail.reply_to_address
        to_addresses = clean_mail.to_addresses
        cc_addresses = clean_mail.cc_addresses
        attachments = clean_mail.attachments
        body_clean = clean_mail.body_clean
        texto =(f"Asunto: {subject}.\nRemitente: {sender_name}.\n"
                f"Dirección del remitente:{sender_address}.\n"
                f"Dirección de respuesta: {reply_to_address}.\n"
                f"Destinatarios: {to_addresses}.\n"
                f"Destinatarios con copia: {cc_addresses}.\n"
                f"Adjuntos: {attachments}.\n"
                f"Cuerpo principal de correo: {body_clean}.") 
        return texto



    

