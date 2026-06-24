"""Review engine — combines static analysis with AI roasting."""
from __future__ import annotations

import json
import random
from dataclasses import dataclass, field

from openai import OpenAI

from roastme.analyzer.engine import AnalysisResult, Category, Finding, Severity
from roastme.config import ROAST_LEVELS, RoastConfig
from roastme.personas.base import get_persona


@dataclass
class LineRoast:
    line: int
    code_snippet: str
    roast: str
    suggestion: str
    category: str


@dataclass
class ReviewResult:
    file_path: str
    overall_roast: str
    line_roasts: list[LineRoast] = field(default_factory=list)
    shame_score: int = 0
    persona_name: str = ""
    summary: str = ""
    refactoring_suggestions: list[str] = field(default_factory=list)


class ReviewEngine:
    """Orchestrates static analysis + AI-powered roasting."""

    def __init__(self, config: RoastConfig):
        self.config = config
        self.client = OpenAI(api_key=config.api_key, base_url=config.api_base)
        self.persona = get_persona(config.persona)
        self.roast_level = ROAST_LEVELS.get(config.roast_level, 2)

    def review(self, file_path: str, source: str, analysis: AnalysisResult) -> ReviewResult:
        """Generate a full roast review for analyzed code."""
        result = ReviewResult(
            file_path=file_path,
            persona_name=self.persona.name,
            shame_score=analysis.shame_score,
        )

        # Build the prompt
        prompt = self._build_prompt(file_path, source, analysis)

        # Get AI roast
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": self.persona.system_prompt},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
            )
            ai_response = response.choices[0].message.content or ""
        except Exception as e:
            ai_response = self._fallback_roast(analysis, str(e))

        # Parse response
        result.overall_roast = ai_response
        result.line_roasts = self._extract_line_roasts(ai_response, analysis)
        result.refactoring_suggestions = self._extract_suggestions(ai_response)
        result.summary = analysis.summary

        return result

    def _build_prompt(self, file_path: str, source: str, analysis: AnalysisResult) -> str:
        level_descriptions = {
            1: "Be gentle. Dad jokes and light teasing only.",
            2: "Be moderately savage. Witty burns, some sarcasm.",
            3: "Go hard. Devastating roasts, no mercy.",
            4: "ABSOLUTELY DESTROY THIS CODE. Nuclear option. Maximum humiliation.",
        }

        # Build findings summary
        findings_text = []
        for f in analysis.findings[:20]:  # Cap at 20 to avoid token overflow
            findings_text.append(
                f"  Line {f.line}: [{f.severity.value.upper()}] {f.category.value} — {f.message}\n"
                f"    Hint: {f.roast_hint}"
            )

        findings_str = "\n".join(findings_text) if findings_text else "  (No issues found... suspicious.)"

        # Select random prefixes/suffixes
        prefix = random.choice(self.persona.roast_prefixes)
        suffix = random.choice(self.persona.roast_suffixes)

        return f"""Review this {analysis.language} file: `{file_path}`

## Static Analysis Results
{findings_str}

## Code
```{analysis.language}
{source}
```

## Instructions
{level_descriptions[self.roast_level]}
Start with: "{prefix}"
End with: "{suffix}"
Include the shame score ({analysis.shame_score}/100) somewhere in your roast.
Provide at least one specific refactoring suggestion.
Be concise (under 200 words). Be HILARIOUS."""

    def _extract_line_roasts(self, ai_response: str, analysis: AnalysisResult) -> list[LineRoast]:
        """Extract per-line roasts from analysis findings."""
        line_roasts = []
        for f in analysis.findings[:10]:
            if f.severity in (Severity.CRITICAL, Severity.WARNING):
                line_roasts.append(LineRoast(
                    line=f.line,
                    code_snippet=f.code_snippet[:60],
                    roast=f.roast_hint or "This line is a crime against computer science.",
                    suggestion=self._category_to_suggestion(f.category),
                    category=f.category.value,
                ))
        return line_roasts

    def _extract_suggestions(self, ai_response: str) -> list[str]:
        """Pull refactoring suggestions from AI response."""
        suggestions = []
        lines = ai_response.split("\n")
        for line in lines:
            stripped = line.strip()
            if any(stripped.lower().startswith(w) for w in ("suggestion:", "refactor:", "recommend:", "try:", "- ")):
                clean = stripped.lstrip("- ").removeprefix("Suggestion:").removeprefix("Refactor:").removeprefix("Recommend:").removeprefix("Try:").strip()
                if clean and len(clean) > 10:
                    suggestions.append(clean)
        if not suggestions:
            suggestions.append("Consider reviewing the flagged lines and applying clean code principles.")
        return suggestions[:5]

    def _category_to_suggestion(self, category: Category) -> str:
        return {
            Category.COMPLEXITY: "Break this into smaller functions. Each should do one thing.",
            Category.ANTI_PATTERN: "Refactor to follow SOLID principles and clean code practices.",
            Category.SECURITY: "Fix this security vulnerability immediately. This is critical.",
            Category.STYLE: "Follow a consistent style guide (PEP8, Prettier, etc.).",
            Category.PERFORMANCE: "Profile and optimize this. Consider caching or better algorithms.",
            Category.NAMING: "Use descriptive names. Future you will thank present you.",
        }.get(category, "Review and improve this code.")

    def _fallback_roast(self, analysis: AnalysisResult, error: str) -> str:
        """Fallback roast when AI is unavailable."""
        prefix = random.choice(self.persona.roast_prefixes)
        suffix = random.choice(self.persona.roast_suffixes)
        return (
            f"{prefix}\n\n"
            f"Your code has a shame score of {analysis.shame_score}/100. "
            f"I found {len(analysis.findings)} issues including "
            f"{sum(1 for f in analysis.findings if f.severity == Severity.CRITICAL)} critical ones.\n\n"
            f"AI roast unavailable ({error}), but honestly, the static analysis alone is damning enough.\n\n"
            f"{suffix}"
        )
