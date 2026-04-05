from __future__ import annotations

import re

from .models import LinearModelParameters, ProblemSpec, TaskType


class VeriflowPlanner:
    _FLOAT_PATTERN = r"-?\\d+(?:\\.\\d+)?"

    def parse_request(self, text: str) -> ProblemSpec:
        lowered = text.lower()
        task_type = self._detect_task_type(lowered)
        parameters = self._extract_parameters(text)
        x_values = self._extract_x_values(text) if task_type == "data_generation" else []
        query_x = self._extract_query_x(text) if task_type == "formula_question_answering" else None
        confidence = self._estimate_confidence(text, task_type, x_values, query_x)

        return ProblemSpec(
            raw_text=text,
            task_type=task_type,
            parameters=parameters,
            x_values=x_values,
            query_x=query_x,
            confidence=confidence,
        )

    def _detect_task_type(self, lowered: str) -> TaskType:
        if "generate" in lowered or "rows" in lowered or "data" in lowered:
            return "data_generation"
        if "what is y" in lowered or "when x" in lowered or "answer" in lowered:
            return "formula_question_answering"
        return "equation_creation"

    def _extract_parameters(self, text: str) -> LinearModelParameters:
        m_value = self._match_named_value(text, "m")
        b_value = self._match_named_value(text, "b")

        formula_match = re.search(
            rf"y\\s*=\\s*({self._FLOAT_PATTERN})\\s*\\*?\\s*x\\s*([+-]\\s*{self._FLOAT_PATTERN})?",
            text,
            flags=re.IGNORECASE,
        )
        if formula_match:
            if m_value is None:
                m_value = float(formula_match.group(1))
            offset = formula_match.group(2)
            if b_value is None and offset:
                b_value = float(offset.replace(" ", ""))

        return LinearModelParameters(
            m=3.0 if m_value is None else m_value,
            b=2.0 if b_value is None else b_value,
        )

    def _match_named_value(self, text: str, symbol: str) -> float | None:
        patterns = [
            rf"\\b{symbol}\\s*=\\s*({self._FLOAT_PATTERN})",
            rf"\\b{symbol}\\s+is\\s+({self._FLOAT_PATTERN})",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return float(match.group(1))
        return None

    def _extract_x_values(self, text: str) -> list[float]:
        pattern = rf"x\\s+values?\\s*(?:of|=|:)?\\s*(({self._FLOAT_PATTERN}(?:\\s*,\\s*{self._FLOAT_PATTERN})*))"
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return [float(part.strip()) for part in match.group(1).split(",")]

        fallback = re.search(
            rf"for\\s+x\\s*(?:=|values?\\s+of\\s+)?(({self._FLOAT_PATTERN}(?:\\s*,\\s*{self._FLOAT_PATTERN})*))",
            text,
            flags=re.IGNORECASE,
        )
        if fallback:
            return [float(part.strip()) for part in fallback.group(1).split(",")]

        return [1.0, 2.0, 3.0, 4.0]

    def _extract_query_x(self, text: str) -> float:
        match = re.search(
            rf"(?:when\\s+x|x)\\s*=\\s*({self._FLOAT_PATTERN})",
            text,
            flags=re.IGNORECASE,
        )
        if match:
            return float(match.group(1))

        fallback = re.search(
            rf"for\\s+x\\s+({self._FLOAT_PATTERN})",
            text,
            flags=re.IGNORECASE,
        )
        if fallback:
            return float(fallback.group(1))

        return 10.0

    def _estimate_confidence(
        self,
        text: str,
        task_type: TaskType,
        x_values: list[float],
        query_x: float | None,
    ) -> float:
        confidence = 0.6
        if "y =" in text.lower() or "m=" in text.lower() or "b=" in text.lower():
            confidence += 0.2
        if task_type == "data_generation" and x_values:
            confidence += 0.1
        if task_type == "formula_question_answering" and query_x is not None:
            confidence += 0.1
        return min(confidence, 0.95)
