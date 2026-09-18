from config.config_app import ConfigApp
from connectors.exchange_service import ExchangeService
from services.logging_service import LoggingService
from services.preprocessor_service import PreprocessorService
from agents.classification.classification_agent import ClassificationAgent
from agents.task_extraction.task_extraction_agent import TaskExtractionAgent

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
    clasificador = ClassificationAgent(config)
    mail_clasificado = clasificador.email_classificator(email)
    print(f"tipo del  objeto 'mail_clasificado': {type(mail_clasificado)}")
    extractor_de_tareas = TaskExtractionAgent(config)
    tareas = extractor_de_tareas.email_extractor(email)
    print(f"tipo del objeto 'tareas': {type(tareas)}")
