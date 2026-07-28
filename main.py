from config.config_app import ConfigApp
from connectors.exchange_service import ExchangeService
from services.logging_service import LoggingService
from services.preprocessor_service import PreprocessorService

LoggingService.configure()

password = input("Password: ")
config = ConfigApp(password)
ingestion = ExchangeService(config)
ingestion.connect()
conexion_existosa = ingestion.test_connection()
recent_emails = ingestion.get_recent_emails(2)
clean_emails_list = []
for email in recent_emails:
    clean_email = PreprocessorService(email)
    clean_emails_list.append(clean_email.clean_rawmail()) 

for email in clean_emails_list:
    print(email.sender_name)
    print(email.received_at)
    print(email.sender_address)
    print(email.subject)
    print(f"cuerpo del mensaje:\n {email.body_clean}")
    print(f"historial:\n {email.quoted_history_clean}")
    print(f"lenguaje:\n {email.language}")
    print(f"Firma: \n {email.signature}")
