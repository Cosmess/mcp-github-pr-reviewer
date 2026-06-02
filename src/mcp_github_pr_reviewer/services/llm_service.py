from typing import Any

import httpx

from mcp_github_pr_reviewer.config import Settings
from mcp_github_pr_reviewer.models import ChangedFile, PullRequest, PullRequestAnalysis


class LLMServiceError(RuntimeError):
    """Raised when the optional LLM analyzer cannot complete."""


class LLMAnalyzerService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def enabled(self) -> bool:
        return self._settings.llm_analyzer_enabled and bool(self._settings.llm_api_key)

    async def enhance_review(
        self,
        pull_request: PullRequest,
        files: list[ChangedFile],
        baseline: PullRequestAnalysis,
    ) -> PullRequestAnalysis:
        if not self.enabled:
            return baseline

        llm_markdown = await self._request_review(pull_request, files, baseline)
        return PullRequestAnalysis(
            summary=baseline.summary,
            important_files=baseline.important_files,
            risks=baseline.risks,
            suggested_tests=baseline.suggested_tests,
            markdown_review=baseline.markdown_review
            + "\n\n## Análise LLM opcional\n\n"
            + llm_markdown.strip(),
        )

    async def _request_review(
        self,
        pull_request: PullRequest,
        files: list[ChangedFile],
        baseline: PullRequestAnalysis,
    ) -> str:
        payload = {
            "model": self._settings.llm_model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Você é um revisor técnico sênior. Analise Pull Requests "
                        "com foco em risco, testes e clareza. Responda em Markdown "
                        "curto, direto e sem inventar arquivos ou comportamento."
                    ),
                },
                {
                    "role": "user",
                    "content": self._build_prompt(pull_request, files, baseline),
                },
            ],
            "temperature": 0.2,
        }

        headers = {
            "Authorization": f"Bearer {self._settings.llm_api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(
            base_url=str(self._settings.llm_api_base_url).rstrip("/"),
            headers=headers,
            timeout=self._settings.llm_timeout_seconds,
        ) as client:
            response = await client.post("/chat/completions", json=payload)

        if response.status_code >= 400:
            raise LLMServiceError(f"LLM API returned {response.status_code}: {response.text[:500]}")

        return self._extract_content(response.json())

    def _build_prompt(
        self,
        pull_request: PullRequest,
        files: list[ChangedFile],
        baseline: PullRequestAnalysis,
    ) -> str:
        patch_context = self._patch_context(files)
        return "\n".join(
            [
                f"PR #{pull_request.number}: {pull_request.title}",
                f"Autor: {pull_request.author}",
                f"Base: {pull_request.base_branch}",
                f"Head: {pull_request.head_branch}",
                "",
                "Resumo heurístico:",
                baseline.markdown_review,
                "",
                "Diff/Patches disponíveis:",
                patch_context,
                "",
                "Gere uma análise complementar com:",
                "- riscos sutis que a análise heurística pode não capturar;",
                "- sugestões de testes mais específicas;",
                "- pontos que merecem atenção humana na revisão.",
            ]
        )

    def _patch_context(self, files: list[ChangedFile]) -> str:
        chunks: list[str] = []
        remaining = self._settings.llm_max_patch_chars
        for file in files:
            if remaining <= 0:
                break

            patch = file.patch or "[patch unavailable]"
            content = (
                f"Arquivo: {file.filename}\n"
                f"Status: {file.status}\n"
                f"Additions: {file.additions}, deletions: {file.deletions}\n"
                f"{patch}\n"
            )
            chunks.append(content[:remaining])
            remaining -= len(content)

        if remaining <= 0:
            chunks.append("\n[LLM patch context truncated by LLM_MAX_PATCH_CHARS]")

        return "\n---\n".join(chunks)

    def _extract_content(self, payload: dict[str, Any]) -> str:
        choices = payload.get("choices") or []
        if not choices:
            raise LLMServiceError("LLM API returned no choices.")

        content = (choices[0].get("message") or {}).get("content")
        if not content:
            raise LLMServiceError("LLM API returned an empty message.")

        return str(content)
