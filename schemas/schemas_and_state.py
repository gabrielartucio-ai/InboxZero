"""
PROYECTO INBOX ZERO - CAPA DE CONTRATOS DE DATOS Y ESTADO
Módulo contendor de las estructuras de datos estructuradas (Pydantic),
restricciones categóricas (Enums) y el estado de la memoria del grafo (TypedDict).
"""

import uuid
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, TypedDict, List
from datetime import datetime

# ==========================================
# 1. RESTRICCIONES CATEGÓRICAS (ENUMS)
# ==========================================

class MailCategory(Enum):
    ACTION_REQUIRED = "Accion requerida"
    INFORMATION = "Informacion"
    FOLLOW_UP = "Seguimiento"
    REQUEST = "Solicitud"
    MEETINGS_AND_EVENTS = "Reuniones y eventos"
    TASKS_AND_COMMITMENTS = "Tareas y compromisos"
    APPROVALS = "Aprobaciones"
    AUTOMATIC_NOTIFICATIONS = "Notificaciones automaticas"
    NEWSLETTERS = "Newsletters"
    PROMOTIONS_AND_MARKETING = "Promociones y Marketing"
    ALERTS = "Alertas"
    PERSONNEL = "Personal"
    SPAM = "Spam"

class RiskLevel(Enum):
    LOW = "Bajo"
    MEDIUM = "Medio"
    HIGH = "Alto" 

class DecisionRegistry(Enum):
    APPROVED = "Aprobado"
    REJECTED = "Rechazado"
    CORRECTED = "Corregido"
    PENDING = "Pendiente"

class FinalStatusOptions(Enum):
    PROCESSED = "Procesado" 
    ARCHIVED = "Archivado" 
    MANUAL_ACTION_REQIRED = "Accion manual requerida"
    SPAM_ISOLATED = "Spam aislado"

# ==========================================
# 2. CONTRATOS DE DATOS DE AGENTES (PYDANTIC)
# ==========================================

class AttachmentInfo(BaseModel):
    attached_filename: str = Field(
        description="Nombre del archivo adjunto."
    )
    attached_content_type: str | None = Field(
        description="Tipo dl contenido del archivo adjunto."
    )
    size: int = Field(
        description="Tamaño del archivo adjunto."
    )
    is_inline: bool = Field(
        description="Booleano que indica si el adjunto está o no en línea"
    )
    content_id: str | None = Field(
        description="Identificador del contenido del archivo adjunto."
    )

class RawMail(BaseModel):
    processing_id: uuid.UUID = Field(
        description="Identificador único del procesamiento del correo dentro " \
        "del workflow."
    )
    provider_message_id: str = Field(
        description="Identificador del mensaje asignado por el proveedor de correo" \
        "(Exchange, Gmail, etc.). Se utiliza para recuperar y ejecutar acciones "
        "sobre el mensaje."
    )
    internet_message_id: str = Field(
        description="Identificador único del mensaje definido por el estándar de correo " \
        "electrónico (RFC 5322). A diferencia del identificador interno del " \
        "proveedor, se conserva durante el transporte entre servidores y permite " \
        "deduplicar mensajes y mantener su trazabilidad incluso cuando cambian de " \
        "plataforma (Exchange, Gmail, IMAP, etc.)."
    )
    conversation_id: str = Field(
        description="Identificador de la conversación o hilo al que pertenece el correo."
    )
    subject: str = Field(
        description="Asunto del mensaje."
    )
    sender_name: str = Field(
        description="Nombre mostrado del remitente."
    )
    sender_address: str = Field(
        description="Dirección de correo electrónico del remitente."
    )
    reply_to_address: str | None = Field(
        description="Dirección de respuesta del mensaje, cuando exista."
    )
    to_addresses: list[str] = Field(
        description="Lista de direcciones de los destinatarios principales."
    )
    cc_addresses: list[str] = Field(
        description="Lista de direcciones de los destinatarios en copia."
    )
    sent_at: datetime = Field(
        description="Fecha y hora de envío del mensaje."
    )
    received_at: datetime = Field(
        description="Fecha y hora de recepción del mensaje en el buzón."
    )
    body_html: str = Field(
        description="Contenido original del mensaje en formato HTML."
    )
    body_text: str = Field(
        description="Contenido original del mensaje en texto plano."
    )
    transport_headers: dict[str, str] = Field(
        description="Encabezados técnicos relevantes del mensaje para análisis y trazabilidad."
    )
    attachments: list[AttachmentInfo] = Field(
        description="Lista de metadatos de los archivos adjuntos."
    )

class CleanMail(BaseModel):
    processing_id: uuid.UUID = Field(
        description="Identificador único del procesamiento del correo."
    )
    provider_message_id: str = Field(
        description="Identificador del mensaje asignado por el proveedor " \
        "de correo. Es elmismo que el de RawMail"
    )
    internet_message_id: str = Field(
        description="Identificador único del mensaje definido por el estándar de correo " \
        "electrónico (RFC 5322). A diferencia del identificador interno del " \
        "proveedor, se conserva durante el transporte entre servidores y permite " \
        "deduplicar mensajes y mantener su trazabilidad incluso cuando cambian de " \
        "plataforma (Exchange, Gmail, IMAP, etc.)."
    )
    conversation_id: str = Field(
        description="Identificador de la conversación o hilo al que pertenece el correo."
    )
    subject: str = Field(
        description="Asunto del mensaje."
    )
    sender_name: str = Field(
        description="Nombre mostrado del remitente."
    )
    sender_address: str = Field(
        description="Dirección de correo electrónico del remitente."
    )
    reply_to_address: str | None = Field(
        description="Dirección de respuesta del mensaje, cuando exista."
    )
    to_addresses: list[str] = Field(
        description="Lista de direcciones de los destinatarios principales."
    )
    cc_addresses: list[str] = Field(
        description="Lista de direcciones de los destinatarios en copia."
    )
    sent_at: datetime = Field(
        description="Fecha y hora de envío del mensaje."
    )
    received_at: datetime = Field(
        description="Fecha y hora de recepción del mensaje en el buzón."
    )
    attachments: list[AttachmentInfo] = Field(
        description="Lista de metadatos de los archivos adjuntos."
    )
    body_clean: str = Field(
        description="Contenido limpio y normalizado del mensaje listo para " \
        "ser procesado por los agentes."
    )
    quoted_history_clean: str = Field(
        description="Historial citado del hilo separado del mensaje principal. " \
        "Es el texto de mensajes anteriores incluido en una respuesta."
    )
    signature: str = Field(
        description="Firma detectada y separada del mensaje."
    )
    language: str = Field(
        description="Idioma detectado del contenido principal."
    )
    truncated: bool = Field(
        description="Indica si el contenido fue truncado durante el " \
        "preprocesamiento."
    )

class MailClassification(BaseModel):
    category: MailCategory = Field(
        description="Seleccionar estrictamente una de las 13 categorías " \
        "predefinidas que mejor describa la naturaleza del correo."
    )
    priority: RiskLevel = Field(
        description="Prioridad operativa del correo (Baja, Media, Alta) basada en el impacto " \
        "que tendría para el usuario o la organización resolver o no resolver " \
        "este correo." 
    )
    urgency: RiskLevel = Field(
        description="Urgencia del correo (Baja, Media, Alta) basada en el tiempo que el " \
        "usuario tiene que actuar" 
    )
    summary: str = Field(
        description="Resumen ejecutivo compacto del correo en un máximo de dos oraciones. " \
        "Tono directo y neutral."
    )
    requires_action: bool = Field(
        description="Indica si el correo requiere alguna accion por parte del usuario"
    )
    classification_confidence: RiskLevel = Field(
        description="Nivel de confianza del agente en la clasificación realizada. Expresa el " \
        "grado de certeza con que considera correcta la categoría y los atributos asignados " \
        "al correo. Es una autoevaluacion realizada por el llm"
    )
    reasoning: str = Field(
        description="Breve justificación de la clasificación realizada."
    )

class SecurityAnalysis(BaseModel):
    is_suspicious: bool = Field(
        description="Establecer en True si el correo muestra patrones claros de phishing, " \
        "fraude, ingeniería social o spam altamente sospechoso."
    )
    risk_level: RiskLevel = Field(
        description="Nivel de riesgo de seguridad estimado para el correo."
    )
    justification: str = Field(
        description="Explicación detallada de los factores semánticos o técnicos que determinaron " \
        "el nivel de riesgo."
    )

class TaskItem(BaseModel):
    task_id: str = Field(
        description="Identificador correlativo temporal generado por el modelo para la tarea "
        "(ej. task_1, task_2)."
    )
    description: str = Field(
        description="Descripción clara, accionable y concisa de la tarea o compromiso identificado " \
        "en el texto."
    )
    due_date: Optional[str] = Field(
        default=None,
        description="Fecha límite explícita o inferida textualmente en el correo (formato YYYY-MM-DD). Si no se menciona, dejar en None."
    )
    assigned_to: str = Field(
        description="Persona encargada de ejecutar la acción. Si está dirigido explícitamente " \
        "al dueño del buzón, indicar 'Usuario'."
    )

class TaskExtraction(BaseModel):
    tasks: List[TaskItem] = Field(
        description="Lista de compromisos o acciones concretas extraídas del correo electrónico. " \
        "Si no hay tareas, devolver lista vacía."
    )
    response_required: bool = Field(
        description="Establecer en True si la naturaleza del correo exige obligatoriamente " \
        "redactar y enviar una respuesta al remitente."
    )

class DraftResponse(BaseModel):
    reply_body: str = Field(
        description="Cuerpo completo propuesto para el correo de respuesta, redactado con un " \
        "tono ejecutivo amable, minimalista y profesional."
    )
    response_type: str = Field(
        description="Breve etiqueta que describe la intención de la respuesta "
        "(ej. 'Confirmación de recepción', 'Solicitud de datos')."
    )
# ==========================================
# 3. ESTADO DEL GRAFO (LANGGRAPH)
# ==========================================

class InboxZeroState(TypedDict):
    """
    Representa la carpeta de memoria intermedia compartida que viaja a través de los nodos del grafo.
    Almacena el estado acumulado del procesamiento de un correo específico.
    """
    raw_mail: dict
    security: Optional[SecurityAnalysis] = None
    classification: Optional[MailClassification] = None
    extracted_tasks: Optional[TaskExtraction] = None
    draft: Optional[DraftResponse] = None
    human_decision: Optional[DecisionRegistry] = DecisionRegistry.PENDING
    final_status: FinalStatusOptions 

        