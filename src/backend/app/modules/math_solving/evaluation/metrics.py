"""
Custom DeepEval metrics for mathematical problem evaluation
"""
import re
import string
from typing import Optional

import openai
from deepeval.metrics.base_metric import BaseMetric
from deepeval.test_case import LLMTestCase


class MathematicalAccuracyMetric(BaseMetric):
    """
    Custom metric to evaluate mathematical answer accuracy with advanced normalization
    and semantic understanding for mathematical expressions
    """

    def __init__(
        self,
        threshold: float = 0.9,
        model: str = "gpt-4.1",
        strict_matching: bool = False,
        include_reason: bool = True,
        use_llm_evaluation: bool = True,
    ):
        self.threshold = threshold
        self.model = model
        self.strict_matching = strict_matching
        self.include_reason = include_reason
        self.use_llm_evaluation = use_llm_evaluation
        self.client = openai.OpenAI() if use_llm_evaluation else None

    def measure(self, test_case: LLMTestCase) -> float:
        """Measure the accuracy of the mathematical answer"""
        expected_answer = test_case.expected_output
        actual_answer = test_case.actual_output

        # Extract answer from actual output if it's a complex response
        actual_clean = self._extract_answer_from_response(actual_answer)

        # Normalize both answers
        expected_normalized = self._normalize_mathematical_answer(expected_answer)
        actual_normalized = self._normalize_mathematical_answer(actual_clean)

        # Calculate score
        if self.strict_matching:
            score = 1.0 if expected_normalized == actual_normalized else 0.0
        else:
            score = self._calculate_similarity_score(
                expected_normalized, actual_normalized
            )

            # Use LLM evaluation for complex cases if enabled
            if score < 0.8 and self.use_llm_evaluation:
                llm_score = self._llm_evaluate_math_equivalence(
                    expected_answer, actual_clean
                )
                score = max(score, llm_score)

        self.score = score
        self.success = score >= self.threshold

        if self.include_reason:
            self.reason = self._generate_reason(expected_answer, actual_clean, score)

        return score

    def _extract_answer_from_response(self, response: str) -> str:
        """Extract the final answer from a complex response"""
        if not response:
            return ""

        # Look for patterns like "Answer: X" or "Final answer: X"
        answer_patterns = [
            r"(?:final\s+)?answer\s*:?\s*([^\n\r]+)",
            r"(?:the\s+)?(?:solution|result)\s+is\s*:?\s*([^\n\r]+)",
            r"therefore\s*,?\s*([^\n\r]+)",
            r"thus\s*,?\s*([^\n\r]+)",
        ]

        for pattern in answer_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # If no pattern found, return the last line that looks like an answer
        lines = response.strip().split("\n")
        for line in reversed(lines):
            line = line.strip()
            if line and not line.endswith("?") and len(line) < 100:
                return line

        return response.strip()

    def _normalize_mathematical_answer(self, answer: str) -> str:
        """Normalize mathematical answers for comparison"""
        if not answer:
            return ""

        # Convert to lowercase and strip
        normalized = answer.lower().strip()

        # Remove common prefixes/suffixes
        prefixes_to_remove = [
            "answer:",
            "solution:",
            "result:",
            "the answer is",
            "final answer:",
        ]
        for prefix in prefixes_to_remove:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix) :].strip()

        # Handle mathematical symbols and formatting
        symbol_replacements = {
            "°": " degrees",
            "∠": "angle ",
            "∆": "triangle ",
            "π": "pi",
            "√": "sqrt",
            "²": "^2",
            "³": "^3",
            "¼": "1/4",
            "½": "1/2",
            "¾": "3/4",
            "∞": "infinity",
        }

        for symbol, replacement in symbol_replacements.items():
            normalized = normalized.replace(symbol, replacement)

        # Normalize fractions
        normalized = self._normalize_fractions(normalized)

        # Normalize percentages
        normalized = self._normalize_percentages(normalized)

        # Normalize units
        normalized = self._normalize_units(normalized)

        # Remove extra whitespace and punctuation
        normalized = re.sub(r"\s+", " ", normalized)
        normalized = normalized.strip(string.punctuation + " ")

        return normalized

    def _normalize_fractions(self, text: str) -> str:
        """Normalize fraction representations"""
        # Convert mixed numbers like "1 1/2" to "3/2"
        mixed_number_pattern = r"(\d+)\s+(\d+)/(\d+)"

        def convert_mixed(match):
            whole, num, den = map(int, match.groups())
            return f"{whole * int(den) + int(num)}/{den}"

        text = re.sub(mixed_number_pattern, convert_mixed, text)

        # Normalize spacing around fractions
        text = re.sub(r"(\d+)\s*/\s*(\d+)", r"\1/\2", text)

        return text

    def _normalize_percentages(self, text: str) -> str:
        """Normalize percentage representations"""
        # Convert "X%" to "X percent"
        text = re.sub(r"(\d+(?:\.\d+)?)\s*%", r"\1 percent", text)
        return text

    def _normalize_units(self, text: str) -> str:
        """Normalize unit representations"""
        unit_mappings = {
            "cm^3": "cubic cm",
            "cm³": "cubic cm",
            "m^2": "square m",
            "m²": "square m",
            "kg": "kilograms",
            "litres": "liters",
            "mins": "minutes",
            "min": "minutes",
        }

        for unit, normalized_unit in unit_mappings.items():
            text = text.replace(unit, normalized_unit)

        return text

    def _calculate_similarity_score(self, expected: str, actual: str) -> float:
        """Calculate similarity score between normalized answers"""
        if expected == actual:
            return 1.0

        # Check if one contains the other
        if expected in actual or actual in expected:
            return 0.9

        # Check for numerical equivalence
        expected_nums = re.findall(r"\d+(?:\.\d+)?", expected)
        actual_nums = re.findall(r"\d+(?:\.\d+)?", actual)

        if expected_nums and actual_nums:
            try:
                expected_val = float(expected_nums[0])
                actual_val = float(actual_nums[0])

                if abs(expected_val - actual_val) < 0.001:
                    return 0.95
                elif (
                    abs(expected_val - actual_val) / max(expected_val, actual_val)
                    < 0.05
                ):
                    return 0.8
            except (ValueError, ZeroDivisionError):
                pass

        # Token-based similarity
        expected_tokens = set(expected.split())
        actual_tokens = set(actual.split())

        if not expected_tokens and not actual_tokens:
            return 1.0
        if not expected_tokens or not actual_tokens:
            return 0.0

        intersection = expected_tokens.intersection(actual_tokens)
        union = expected_tokens.union(actual_tokens)

        return len(intersection) / len(union)

    def _llm_evaluate_math_equivalence(self, expected: str, actual: str) -> float:
        """Use LLM to evaluate mathematical equivalence"""
        if not self.client:
            return 0.0

        prompt = f"""
        As a mathematics expert, evaluate whether these two mathematical answers are equivalent:

        Expected Answer: {expected}
        Actual Answer: {actual}

        Consider:
        - Mathematical equivalence (e.g., 1/2 = 0.5 = 50%)
        - Different but valid representations
        - Rounding differences within reasonable bounds
        - Unit conversions

        Respond with only a score from 0.0 to 1.0, where:
        - 1.0 = Mathematically equivalent
        - 0.8-0.9 = Very close (minor formatting/rounding differences)
        - 0.5-0.7 = Partially correct
        - 0.0-0.4 = Incorrect

        Score:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=10,
            )

            score_text = response.choices[0].message.content.strip()
            score = float(re.findall(r"\d+\.\d+|\d+", score_text)[0])
            return min(max(score, 0.0), 1.0)

        except Exception:
            return 0.0

    def _generate_reason(self, expected: str, actual: str, score: float) -> str:
        """Generate explanation for the score"""
        if score >= 0.95:
            return f"Excellent match (score: {score:.2f}). Expected: '{expected}', Got: '{actual}'"
        elif score >= 0.8:
            return f"Good match (score: {score:.2f}). Expected: '{expected}', Got: '{actual}'"
        elif score >= 0.5:
            return f"Partial match (score: {score:.2f}). Expected: '{expected}', Got: '{actual}'"
        else:
            return f"Poor match (score: {score:.2f}). Expected: '{expected}', Got: '{actual}'"

    def is_successful(self) -> bool:
        """Check if the metric passed the threshold"""
        return self.success

    @property
    def __name__(self):
        return "Mathematical Accuracy"


class MathSolutionCompletenessMetric(BaseMetric):
    """
    Metric to evaluate the completeness of mathematical solutions
    (presence of steps, explanations, etc.)
    """

    def __init__(self, threshold: float = 0.7, include_reason: bool = True):
        self.threshold = threshold
        self.include_reason = include_reason

    def measure(self, test_case: LLMTestCase) -> float:
        """Measure the completeness of the solution"""
        actual_output = test_case.actual_output

        completeness_score = 0.0
        components = []

        # Check for final answer (40% weight)
        if self._has_final_answer(actual_output):
            completeness_score += 0.4
            components.append("final answer")

        # Check for solution steps (30% weight)
        if self._has_solution_steps(actual_output):
            completeness_score += 0.3
            components.append("solution steps")

        # Check for explanation (20% weight)
        if self._has_explanation(actual_output):
            completeness_score += 0.2
            components.append("explanation")

        # Check for mathematical reasoning (10% weight)
        if self._has_mathematical_reasoning(actual_output):
            completeness_score += 0.1
            components.append("mathematical reasoning")

        self.score = completeness_score
        self.success = completeness_score >= self.threshold

        if self.include_reason:
            self.reason = f"Solution completeness: {completeness_score:.2f}. Contains: {', '.join(components) if components else 'minimal components'}"

        return completeness_score

    def _has_final_answer(self, text: str) -> bool:
        """Check if the response contains a clear final answer"""
        answer_indicators = [
            "answer",
            "solution",
            "result",
            "therefore",
            "thus",
            "final",
            "conclusion",
            "equals",
            "=",
            "is",
        ]
        return any(indicator in text.lower() for indicator in answer_indicators)

    def _has_solution_steps(self, text: str) -> bool:
        """Check if the response contains solution steps"""
        step_indicators = [
            "step",
            "first",
            "second",
            "next",
            "then",
            "now",
            "calculate",
            "substitute",
            "solve",
            "simplify",
            "factor",
        ]
        return any(indicator in text.lower() for indicator in step_indicators)

    def _has_explanation(self, text: str) -> bool:
        """Check if the response contains explanations"""
        explanation_indicators = [
            "because",
            "since",
            "due to",
            "reason",
            "explain",
            "why",
            "how",
            "method",
            "approach",
            "concept",
            "principle",
        ]
        return any(indicator in text.lower() for indicator in explanation_indicators)

    def _has_mathematical_reasoning(self, text: str) -> bool:
        """Check if the response contains mathematical reasoning"""
        reasoning_indicators = [
            "theorem",
            "formula",
            "equation",
            "property",
            "rule",
            "law",
            "identity",
            "relationship",
            "pattern",
        ]
        return any(indicator in text.lower() for indicator in reasoning_indicators)

    def is_successful(self) -> bool:
        return self.success

    @property
    def __name__(self):
        return "Solution Completeness"


class MathConfidenceMetric(BaseMetric):
    """
    Metric to evaluate the confidence score provided by the math solver
    """

    def __init__(self, threshold: float = 0.7, include_reason: bool = True):
        self.threshold = threshold
        self.include_reason = include_reason

    def measure(self, test_case: LLMTestCase) -> float:
        """Measure the appropriateness of confidence score"""
        # This would need to be adapted based on how confidence is provided
        # For now, we'll use a placeholder implementation

        actual_output = test_case.actual_output

        # Extract confidence if present in the output
        confidence = self._extract_confidence(actual_output)

        if confidence is None:
            # No confidence provided
            self.score = 0.5
            self.reason = "No confidence score provided"
        else:
            # Evaluate if confidence is reasonable
            # This is a simplified evaluation - you might want more sophisticated logic
            self.score = min(confidence + 0.2, 1.0)  # Bonus for providing confidence
            self.reason = f"Confidence score provided: {confidence}"

        self.success = self.score >= self.threshold
        return self.score

    def _extract_confidence(self, text: str) -> Optional[float]:
        """Extract confidence score from text"""
        # Look for patterns like "confidence: 0.85" or "85% confident"
        confidence_patterns = [
            r"confidence\s*:?\s*(\d+(?:\.\d+)?)",
            r"(\d+(?:\.\d+)?)\s*%?\s*confident",
            r"certainty\s*:?\s*(\d+(?:\.\d+)?)",
        ]

        for pattern in confidence_patterns:
            match = re.search(pattern, text.lower())
            if match:
                value = float(match.group(1))
                # Convert percentage to decimal if needed
                if value > 1:
                    value = value / 100
                return value

        return None

    def is_successful(self) -> bool:
        return self.success

    @property
    def __name__(self):
        return "Confidence Appropriateness"
