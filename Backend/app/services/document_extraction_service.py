import re


class MedicalDocumentExtractionService:

    def extract(
        self,
        ocr_text: str
    ) -> dict:

        if not ocr_text or not ocr_text.strip():
            raise ValueError(
                "OCR text cannot be empty"
            )

        return {
            "diagnoses": self._extract_diagnoses(ocr_text),
            "medications": self._extract_medications(ocr_text),
            "lab_results": self._extract_lab_results(ocr_text),
            "procedures": self._extract_procedures(ocr_text),
            "dates": self._extract_dates(ocr_text)
        }

    def _extract_diagnoses(
        self,
        text: str
    ) -> list[str]:

        patterns = [
            r"diagnosis\s*[:\-]\s*(.+)",
            r"diagnoses\s*[:\-]\s*(.+)",
            r"condition\s*[:\-]\s*(.+)"
        ]

        return self._extract_labeled_values(
            text,
            patterns
        )

    def _extract_medications(
        self,
        text: str
    ) -> list[str]:

        patterns = [
            r"medication\s*[:\-]\s*(.+)",
            r"medications\s*[:\-]\s*(.+)",
            r"medicine\s*[:\-]\s*(.+)",
            r"medicines\s*[:\-]\s*(.+)"
        ]

        return self._extract_labeled_values(
            text,
            patterns
        )

    def _extract_lab_results(
        self,
        text: str
    ) -> list[str]:

        patterns = [
            r"lab\s*result\s*[:\-]\s*(.+)",
            r"lab\s*results\s*[:\-]\s*(.+)",
            r"test\s*result\s*[:\-]\s*(.+)"
        ]

        return self._extract_labeled_values(
            text,
            patterns
        )

    def _extract_procedures(
        self,
        text: str
    ) -> list[str]:

        patterns = [
            r"procedure\s*[:\-]\s*(.+)",
            r"procedures\s*[:\-]\s*(.+)",
            r"surgery\s*[:\-]\s*(.+)"
        ]

        return self._extract_labeled_values(
            text,
            patterns
        )

    def _extract_dates(
        self,
        text: str
    ) -> list[str]:

        date_patterns = [
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
            r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",
            r"\b\d{1,2}\s+"
            r"(?:January|February|March|April|May|June|July|"
            r"August|September|October|November|December)"
            r"\s+\d{4}\b"
        ]

        dates = []

        for pattern in date_patterns:
            matches = re.findall(
                pattern,
                text,
                flags=re.IGNORECASE
            )

            dates.extend(matches)

        return self._unique_values(dates)

    def _extract_labeled_values(
        self,
        text: str,
        patterns: list[str]
    ) -> list[str]:

        values = []

        for pattern in patterns:
            matches = re.findall(
                pattern,
                text,
                flags=re.IGNORECASE
            )

            for match in matches:
                value = match.strip()

                if value:
                    values.append(value)

        return self._unique_values(values)

    def _unique_values(
        self,
        values: list[str]
    ) -> list[str]:

        unique_values = []
        seen = set()

        for value in values:
            normalized = value.strip()

            if not normalized:
                continue

            key = normalized.lower()

            if key in seen:
                continue

            seen.add(key)
            unique_values.append(normalized)

        return unique_values


document_extraction_service = (
    MedicalDocumentExtractionService()
)