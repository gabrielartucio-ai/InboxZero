import html2text

from schemas.schemas_and_state import RawMail, CleanMail
from detectors.quoted_history_detector import QuotedHistoryDetector
from lingua import LanguageDetectorBuilder
from detectors.signature_detector import SignatureDetector

class PreprocessorService:
    """
    Normaliza un correo recibido en formato RawMail y construye un CleanMail.

    Responsabilidades:
    - Conservar los metadatos y los identificadores de trazabilidad.
    - Convertir el cuerpo HTML a Markdown.
    - Separar el mensaje actual del historial citado.
    - Separar la firma del cuerpo principal.
    - Detectar el idioma del contenido principal.
    - Informar si el contenido fue truncado.
    """

    def __init__(self, raw_mail: RawMail):
        """Inicializa el servicio con el correo original que será procesado."""
        self.raw_mail = raw_mail

    def clean_rawmail(self) -> CleanMail:
        """
        Ejecuta el preprocesamiento completo y devuelve un CleanMail.
        """

        # Se conservan los identificadores originales durante todo el workflow.
        processing_id = self.raw_mail.processing_id
        provider_message_id = self.raw_mail.provider_message_id
        internet_message_id = self.raw_mail.internet_message_id
        conversation_id = self.raw_mail.conversation_id

        # Se copian los metadatos funcionales sin modificarlos.
        subject = self.raw_mail.subject
        sender_name = self.raw_mail.sender_name
        sender_address = self.raw_mail.sender_address
        reply_to_address = self.raw_mail.reply_to_address
        to_addresses = self.raw_mail.to_addresses
        cc_addresses = self.raw_mail.cc_addresses
        sent_at = self.raw_mail.sent_at
        received_at = self.raw_mail.received_at
        attachments = self.raw_mail.attachments

        # Se convierte el HTML original a Markdown.
        body_markdown = self._html_cleaner()

        # Se separa el mensaje actual del historial citado.
        quoted_history_detector = QuotedHistoryDetector()
        body_clean, quoted_history_clean = quoted_history_detector.separate(
            body_markdown
        )

        # Se busca la firma únicamente en el mensaje actual.
        signature_detector = SignatureDetector()
        body_clean, signature = signature_detector.separate(
            body_clean,
            sender_name
        )

        # Se detecta el idioma después de separar historial y firma.
        language = self._detect_language(body_clean)

        # En esta versión todavía no se aplica truncamiento.
        truncated = False

        # Se construye el contrato normalizado de salida.
        clean_mail = CleanMail(
            processing_id=processing_id,
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
            attachments=attachments,
            body_clean=body_clean,
            quoted_history_clean=quoted_history_clean,
            signature=signature,
            language=language,
            truncated=truncated
        )

        return clean_mail

    def _html_cleaner(self) -> str:
        """Convierte el cuerpo HTML original a Markdown."""
        parser = html2text.HTML2Text()

        # No conserva las URLs de los enlaces.
        parser.ignore_links = True

        # Ignora las imágenes incrustadas en el HTML.
        parser.ignore_images = True

        # Evita saltos de línea automáticos por ancho máximo.
        parser.body_width = 0

        return parser.handle(self.raw_mail.body_html)

    def _detect_language(self, body: str) -> str:
        """
        Devuelve el código ISO 639-1 del idioma detectado.

        Retorna ``unknown`` cuando el cuerpo está vacío o no puede detectarse.
        """
        if not body:
            return "unknown"

        detector = LanguageDetectorBuilder.from_all_languages().build()
        language = detector.detect_language_of(body)

        if language is None:
            return "unknown"

        return language.iso_code_639_1.name.lower()

    def is_truncated():
        """Método reservado para implementar el control de truncamiento."""
        pass
