import re

class QuotedHistoryDetector:
    """
    Detecta y separa el historial citado de un correo electrónico.

    La clase trabaja sobre el cuerpo del mensaje ya convertido a Markdown.
    Busca distintos formatos habituales generados por Outlook, Exchange,
    Gmail y otros clientes de correo.
    """

    # Patrones que indican el comienzo probable del historial citado.
    # Se utiliza una variable de clase porque todos los objetos comparten
    # exactamente las mismas reglas de detección.
    QUOTED_HISTORY_PATTERNS = [
        # Outlook / Exchange convertido a Markdown:
        # **De:** remitente
        # **From:** sender
        r"(?im)^\s*\*{0,2}de:\*{0,2}\s+",
        r"(?im)^\s*\*{0,2}from:\*{0,2}\s+",

        # Separadores clásicos en español e inglés.
        r"(?im)^-{2,}\s*mensaje original\s*-{2,}",
        r"(?im)^-{2,}\s*original message\s*-{2,}",

        # Línea formada por varios guiones bajos.
        r"(?im)^_{5,}",

        # Formatos habituales de Gmail, Apple Mail y otros clientes.
        r"(?im)^on .+ wrote:",
        r"(?im)^el .+ escribió:",
    ]

    def separate(self, body: str) -> tuple[str, str]:
        """
        Separa el mensaje actual del historial citado.

        Args:
            body: Cuerpo completo del correo en formato Markdown.

        Returns:
            tuple[str, str]:
                - Primer elemento: cuerpo actual del mensaje.
                - Segundo elemento: historial citado.

            Si no se encuentra historial, devuelve el cuerpo completo
            y una cadena vacía.
        """
        if not body:
            return "", ""

        # Busca la primera posición donde aparece un patrón de historial.
        separator_position = self._find_separator_position(body)

        # Si no se detecta ningún separador, todo el texto pertenece
        # al mensaje actual.
        if separator_position is None:
            return body.strip(), ""

        # Todo lo anterior al separador es el mensaje actual.
        body_current = body[:separator_position].strip()

        # Desde el separador en adelante se considera historial citado.
        quoted_history = body[separator_position:].strip()

        return body_current, quoted_history

    def _find_separator_position(self, body: str) -> int | None:
        """
        Busca todas las coincidencias posibles y devuelve la primera.

        Args:
            body: Cuerpo completo del correo.

        Returns:
            int | None:
                Posición donde comienza el historial citado, o None
                cuando no se encuentra ningún patrón.
        """
        positions = []

        # Se prueba cada patrón de detección sobre el cuerpo completo.
        for pattern in self.QUOTED_HISTORY_PATTERNS:
            match = re.search(pattern, body)

            # Si hubo coincidencia, se guarda la posición inicial.
            if match:
                positions.append(match.start())

        # Ningún patrón coincidió.
        if not positions:
            return None

        # Si aparecen varios separadores, se utiliza el primero,
        # porque marca el comienzo del historial más cercano
        # al mensaje actual.
        return min(positions)
