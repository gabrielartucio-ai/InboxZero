"""
Responsabilidad del agente:
- autenticarse
- conectarse a EWS
- consultar mailbox
- recuperar mails
- listar mails
- leer metadata básica
- devolver estructura limpia
"""
import logging
import uuid
from config.config_app import ConfigApp
from connectors.source_connector_interface import SourceConnectorInterface
from schemas.schemas_and_state import RawMail, AttachmentInfo
from exchangelib import Credentials, Account, Configuration, DELEGATE

logger = logging.getLogger(__name__)

class ExchangeService(SourceConnectorInterface):

    def __init__(self, config: ConfigApp):
        super().__init__(config)
        self.cuenta = None

    def connect(self) -> None:
        credenciales = Credentials(
            username = self.config.USERNAME,
            password = self.config.PASSWORD
        )
        mail_config = Configuration(
            service_endpoint=self.config.MAIL_SERVER_URL,
            credentials=credenciales
        )
        try:
            self.cuenta = Account(
                primary_smtp_address=self.config.EMAIL_ADDRESS,
                config=mail_config,
                access_type = DELEGATE,
                autodiscover=False
            )
            self.connected = True
            logger.info(
                "Conexión con Exchange establecida. Cuenta=%s",
                self.config.EMAIL_ADDRESS
            )

        except Exception:
            self.connected = False
            self.cuenta = None
            logger.exception(
                "Error al conectar con el servidor Exchange. "
                "Servidor=%s, cuenta=%s",
                self.config.MAIL_SERVER_URL,
                self.config.EMAIL_ADDRESS
            )
            raise

    def get_recent_emails(self, cantidad: int) -> list[RawMail]:
        self._validate_limit(cantidad)
        if not self.connected or self.cuenta is None:
            raise RuntimeError(
                "ExchangeService no está conectado. Debe ejecutar connect() primero."
            )

        try:
            mail_list = []
            ordered_query_set = self.cuenta.inbox.all().order_by("-datetime_received")
            recent_mails = ordered_query_set[:cantidad]
            for message in recent_mails:
                processing_id = uuid.uuid4()
                #El identificador EWS puede cambiar cuando el mensaje se mueve a otra 
                #carpeta. Por ejemplo, al moverlo de Bandeja de entrada a Archivo, 
                #Exchange puede asignarle otro ItemId.
                provider_message_id = message.id
                internet_message_id = message.message_id
                conversation_id = message.conversation_id.id
                subject = message.subject
                sender = message.author
                sender_name = sender.name
                sender_address = sender.email_address
                reply_to_address = (
                    message.reply_to[0].email_address
                    if message.reply_to
                    else None
                )
                to_addresses = [
                    address.email_address
                    for address in (message.to_recipients or [])
                ]
                cc_addresses = [
                    address.email_address
                    for address in (message.cc_recipients or [])
                ]
                raw_datetime = message.datetime_received
                local_date = raw_datetime.astimezone(self.cuenta.default_timezone)
                sent_at = message.datetime_sent
                received_at = local_date 
                body_html = str(message.body)
                body_text = ""
                transport_headers = {
                    header.name: header.value
                    for header in (message.headers or [])
                }
                attachments_list = []
                for attachment in message.attachments:
                    attached_filename = attachment.name
                    attached_content_type = attachment.content_type
                    size = attachment.size
                    is_inline = attachment.is_inline
                    content_id = attachment.content_id
                    file_attached = AttachmentInfo(attached_filename=attached_filename,
                                                attached_content_type=attached_content_type,
                                                size=size,
                                                is_inline=is_inline,
                                                content_id=content_id
                    )
                    attachments_list.append(file_attached)
                raw_mail = RawMail(processing_id=processing_id,
                                provider_message_id=provider_message_id,
                                internet_message_id=internet_message_id,
                                conversation_id=conversation_id,
                                subject=subject,
                                sender_name=sender_name,
                                sender_address=sender_address,
                                reply_to_address=reply_to_address,
                                to_addresses=to_addresses, 
                                cc_addresses=cc_addresses,
                                sent_at=sent_at,
                                received_at=received_at,
                                body_html=body_html,
                                body_text=body_text,
                                transport_headers=transport_headers,
                                attachments=attachments_list
                )
                mail_list.append(raw_mail)
            logger.info(
                "Se recuperaron %d correos de Exchange.",
                len(mail_list)
            )
            return mail_list

        except Exception:
            logger.exception(
                "Error al recuperar correos de Exchange. "
                "Cuenta=%s, cantidad_solicitada=%d",
                self.config.EMAIL_ADDRESS,
                cantidad
            )
            raise
    
    def test_connection(self) -> bool:
        return self.connected and self.cuenta is not None    
        
