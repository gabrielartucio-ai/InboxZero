import re
import unicodedata

class SignatureDetector:
    """
    Detecta y separa la firma del cuerpo principal de un correo.

    La detección se basa en heurísticas:
    - separadores estándar de firma;
    - despedidas frecuentes;
    - coincidencia con el nombre del remitente;
    - presencia de teléfonos, correos electrónicos o URLs.

    El objetivo es ser conservador: si no hay evidencia suficiente,
    se conserva todo el texto como cuerpo principal y la firma queda vacía.
    """

    # Despedidas habituales en español e inglés.
    # Se almacenan como patrones porque luego se evalúan con expresiones regulares.
    FAREWELL_PATTERNS = [
        r"saludos",
        r"saludos cordiales",
        r"cordialmente",
        r"atentamente",
        r"muchas gracias",
        r"gracias",
        r"un saludo",
        r"un cordial saludo",
        r"sds",
        r"regards",
        r"best regards",
        r"kind regards",
        r"sincerely",
        r"thanks",
        r"thank you",
    ]

    # Cantidad máxima de líneas finales que se inspeccionan buscando la firma.
    MAX_SIGNATURE_LINES = 12

    def separate(
        self,
        body: str,
        sender_name: str | None = None
    ) -> tuple[str, str]:
        """
        Separa el cuerpo principal de la firma.

        Args:
            body: Cuerpo actual del mensaje, sin historial citado.
            sender_name: Nombre del remitente, cuando está disponible.

        Returns:
            tuple[str, str]:
                - Primer elemento: cuerpo sin firma.
                - Segundo elemento: firma detectada.

            Si no se detecta una firma, devuelve el cuerpo completo
            y una cadena vacía.
        """
        if not body or not body.strip():
            return "", ""

        # Divide el texto en líneas para analizar el bloque final del mensaje.
        lines = body.strip().splitlines()

        # Busca la posición donde probablemente comienza la firma.
        signature_start = self._find_signature_start(
            lines=lines,
            sender_name=sender_name
        )

        # Si no se detecta una firma, se conserva el cuerpo completo.
        if signature_start is None:
            return body.strip(), ""

        # Todo lo anterior al comienzo de la firma permanece en el cuerpo.
        body_without_signature = "\n".join(
            lines[:signature_start]
        ).strip()

        # Desde la posición detectada hasta el final se considera firma.
        signature = "\n".join(
            lines[signature_start:]
        ).strip()

        return body_without_signature, signature

    def _find_signature_start(
        self,
        lines: list[str],
        sender_name: str | None
    ) -> int | None:
        """
        Busca el índice de la línea donde comienza la firma.

        Aplica las reglas en este orden:
        1. Separador estándar ``--``.
        2. Despedida conocida cercana al final.
        3. Nombre del remitente al final del mensaje.
        """

        # Limita la búsqueda al bloque final del correo.
        search_start = max(
            0,
            len(lines) - self.MAX_SIGNATURE_LINES
        )

        # 1. Busca el separador estándar de firma.
        for index in range(search_start, len(lines)):
            if lines[index].strip() == "--":
                return index

        # 2. Busca despedidas desde el final hacia arriba.
        # Esto permite elegir la despedida más cercana a la firma.
        for index in range(len(lines) - 1, search_start - 1, -1):
            normalized_line = self._normalize_line(lines[index])

            if self._is_farewell(normalized_line):
                remaining_lines = lines[index:]

                # Solo se acepta la despedida si el bloque posterior
                # presenta características razonables de una firma.
                if self._looks_like_signature(
                    remaining_lines,
                    sender_name
                ):
                    # La despedida queda en el cuerpo principal.
                    # La firma comienza en la siguiente línea no vacía.
                    return self._next_non_empty_line(lines, index + 1)

        # 3. Si no hubo despedida, intenta localizar el nombre del remitente.
        if sender_name:
            name_position = self._find_sender_name(
                lines,
                sender_name,
                search_start
            )

            if name_position is not None:
                return name_position

        return None

    @staticmethod
    def _next_non_empty_line(
        lines: list[str],
        start_index: int
    ) -> int | None:
        """
        Devuelve el índice de la siguiente línea que contiene texto.
        """
        for index in range(start_index, len(lines)):
            if lines[index].strip():
                return index

        return None

    def _find_sender_name(
        self,
        lines: list[str],
        sender_name: str,
        search_start: int
    ) -> int | None:
        """
        Busca el nombre completo o el primer nombre del remitente
        dentro de las últimas líneas del correo.
        """

        # Normaliza el nombre para comparar sin mayúsculas ni tildes.
        normalized_full_name = self._normalize_text(sender_name)
        name_parts = normalized_full_name.split()

        if not name_parts:
            return None

        first_name = name_parts[0]

        # Recorre las líneas desde el final hacia arriba.
        for index in range(len(lines) - 1, search_start - 1, -1):
            normalized_line = self._normalize_text(lines[index])

            if not normalized_line:
                continue

            # Coincidencia con el nombre completo.
            if normalized_line == normalized_full_name:
                return index

            # Coincidencia con el primer nombre.
            if normalized_line == first_name:
                return index

        return None

    def _is_farewell(self, line: str) -> bool:
        """
        Indica si una línea coincide con una despedida conocida.
        """
        for pattern in self.FAREWELL_PATTERNS:
            if re.fullmatch(
                rf"{pattern}[\s,.:;!]*",
                line,
                flags=re.IGNORECASE
            ):
                return True

        return False

    def _looks_like_signature(
        self,
        lines: list[str],
        sender_name: str | None
    ) -> bool:
        """
        Evalúa si el bloque posterior a una despedida parece una firma.

        Se consideran señales:
        - correo electrónico;
        - teléfono;
        - URL;
        - presencia del nombre del remitente;
        - cantidad razonable de líneas.
        """

        # Elimina líneas vacías para analizar solamente contenido útil.
        non_empty_lines = [
            line.strip()
            for line in lines
            if line.strip()
        ]

        # Una despedida sin contenido posterior no se considera firma.
        if len(non_empty_lines) < 2:
            return False

        block = "\n".join(non_empty_lines)

        # Cualquiera de estas señales fuertes alcanza para aceptar el bloque.
        if self._contains_email(block):
            return True

        if self._contains_phone(block):
            return True

        if self._contains_url(block):
            return True

        # También se acepta si aparece el nombre del remitente.
        if sender_name:
            normalized_sender = self._normalize_text(sender_name)
            normalized_block = self._normalize_text(block)
            first_name = normalized_sender.split()[0]

            if (
                normalized_sender in normalized_block
                or first_name in normalized_block.split()
            ):
                return True

        # Como última heurística, se acepta un bloque breve.
        return 2 <= len(non_empty_lines) <= self.MAX_SIGNATURE_LINES

    @staticmethod
    def _normalize_line(line: str) -> str:
        """
        Normaliza espacios y mayúsculas de una línea.
        """
        return re.sub(r"\s+", " ", line).strip().lower()

    @staticmethod
    def _normalize_text(text: str) -> str:
        """
        Normaliza un texto para facilitar comparaciones.

        Elimina:
        - diferencias entre mayúsculas y minúsculas;
        - tildes y otros signos diacríticos;
        - signos finales de puntuación;
        - espacios repetidos.
        """
        text = text.strip().lower()

        # Convierte caracteres acentuados a su forma base.
        text = "".join(
            character
            for character in unicodedata.normalize("NFD", text)
            if unicodedata.category(character) != "Mn"
        )

        # Elimina signos finales, por ejemplo en ``Luis.``.
        text = re.sub(r"[.,:;!?]+$", "", text)

        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def _contains_email(text: str) -> bool:
        """
        Indica si el bloque contiene una dirección de correo electrónico.
        """
        pattern = r"\b[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}\b"
        return re.search(pattern, text) is not None

    @staticmethod
    def _contains_phone(text: str) -> bool:
        """
        Indica si el bloque contiene una referencia o número telefónico.
        """

        # Busca etiquetas habituales de teléfono.
        label_pattern = (
            r"(?i)\b("
            r"tel|teléfono|telefono|cel|celular|móvil|movil|"
            r"phone|mobile"
            r")\b"
        )

        if re.search(label_pattern, text):
            return True

        # Busca secuencias numéricas con formato razonable de teléfono.
        number_pattern = r"(?:\+?\d[\d\s().-]{6,}\d)"
        return re.search(number_pattern, text) is not None

    @staticmethod
    def _contains_url(text: str) -> bool:
        """
        Indica si el bloque contiene una URL.
        """
        pattern = r"(?i)\b(?:https?://|www\.)\S+"
        return re.search(pattern, text) is not None
