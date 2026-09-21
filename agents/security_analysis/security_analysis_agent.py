from config.config_app import ConfigApp
from llm.llm_gateway import LLMGateway
from schemas.schemas_and_state import CleanMail, SecurityAnalysis
from agents.security_analysis.prompts import build_security_analysis_system_prompt

AGENT_ID = "security_analysis_agent" 

class SecurityAnalysisAgent:
    def __init__(self, config: ConfigApp):
        self.llm_gateway = LLMGateway(config=config, agent_id=AGENT_ID)
        self.system_prompt = build_security_analysis_system_prompt()

    def email_security_analyzer(self, clean_mail: CleanMail) -> SecurityAnalysis:
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
        return (
            f"Asunto: {clean_mail.subject}\n"
            f"Remitente: {clean_mail.sender_name} <{clean_mail.sender_address}>\n"
            f"Responder a: {clean_mail.reply_to_address or 'N/A'}\n"
            f"Destinatarios: {', '.join(clean_mail.to_addresses)}\n"
            f"Copia (CC): {', '.join(clean_mail.cc_addresses)}\n"
            f"Archivos Adjuntos: {clean_mail.attachments}\n\n"
            f"Cuerpo del Correo:\n{clean_mail.body_clean}"
        )

