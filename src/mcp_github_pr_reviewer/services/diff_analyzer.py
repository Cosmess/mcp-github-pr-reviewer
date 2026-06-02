from mcp_github_pr_reviewer.models import ChangedFile, PullRequest, PullRequestAnalysis


class DiffAnalyzer:
    critical_path_fragments = (
        "auth",
        "security",
        "payment",
        "payments",
        "settlement",
        "database",
        "migration",
        "infra",
        "config",
        "middleware",
    )

    test_path_fragments = ("test", "tests", "spec", "__tests__")

    def analyze(self, pull_request: PullRequest, files: list[ChangedFile]) -> PullRequestAnalysis:
        important_files = self._important_files(files)
        risks = self._risks(files)
        suggested_tests = self._suggest_tests(files)
        summary = self._summary(pull_request, files)
        markdown_review = self._markdown_review(summary, important_files, risks, suggested_tests)

        return PullRequestAnalysis(
            summary=summary,
            important_files=important_files,
            risks=risks,
            suggested_tests=suggested_tests,
            markdown_review=markdown_review,
        )

    def _summary(self, pull_request: PullRequest, files: list[ChangedFile]) -> str:
        total_additions = sum(file.additions for file in files)
        total_deletions = sum(file.deletions for file in files)
        return (
            f"PR #{pull_request.number} altera {len(files)} arquivo(s), "
            f"com {total_additions} adição(ões) e {total_deletions} remoção(ões). "
            f"Título: {pull_request.title}"
        )

    def _important_files(self, files: list[ChangedFile]) -> list[str]:
        ranked = sorted(files, key=lambda item: item.changes, reverse=True)
        important = [
            file.filename
            for file in ranked
            if file.changes >= 50 or self._has_fragment(file.filename, self.critical_path_fragments)
        ]
        return important[:10]

    def _risks(self, files: list[ChangedFile]) -> list[str]:
        risks: list[str] = []
        if any(self._has_fragment(file.filename, ("migration", "schema")) for file in files):
            risks.append(
                "Mudanças em schema/migrations podem exigir validação de rollback e dados."
            )
        if any(
            self._has_fragment(file.filename, ("auth", "security", "permission"))
            for file in files
        ):
            risks.append("Mudanças em autenticação/autorização podem afetar controle de acesso.")
        if any(
            self._has_fragment(file.filename, ("payment", "settlement", "invoice"))
            for file in files
        ):
            risks.append("Mudanças em fluxo financeiro podem impactar conciliação ou liquidação.")
        if sum(file.changes for file in files) > 500:
            risks.append("PR grande: maior risco de regressão e revisão parcial.")
        if not any(self._has_fragment(file.filename, self.test_path_fragments) for file in files):
            risks.append("Nenhum arquivo de teste foi alterado no PR.")

        return risks or ["Nenhum risco evidente foi identificado pela análise heurística."]

    def _suggest_tests(self, files: list[ChangedFile]) -> list[str]:
        suggestions = ["Executar a suíte automatizada relacionada aos módulos alterados."]
        if any(self._has_fragment(file.filename, ("api", "controller", "route")) for file in files):
            suggestions.append(
                "Adicionar ou revisar testes de contrato/API para os endpoints alterados."
            )
        if any(
            self._has_fragment(file.filename, ("service", "use_case", "handler"))
            for file in files
        ):
            suggestions.append(
                "Adicionar testes unitários para regras de negócio e cenários de borda."
            )
        if any(self._has_fragment(file.filename, ("migration", "schema")) for file in files):
            suggestions.append("Validar migration em base local e cenário de rollback.")
        if any(
            self._has_fragment(file.filename, ("payment", "settlement", "invoice"))
            for file in files
        ):
            suggestions.append(
                "Cobrir cenários financeiros de sucesso, falha, duplicidade e divergência."
            )

        return suggestions

    def _markdown_review(
        self,
        summary: str,
        important_files: list[str],
        risks: list[str],
        suggested_tests: list[str],
    ) -> str:
        return "\n".join(
            [
                "## Resumo técnico",
                "",
                summary,
                "",
                "## Arquivos principais",
                "",
                self._markdown_list(important_files),
                "",
                "## Riscos encontrados",
                "",
                self._markdown_list(risks),
                "",
                "## Testes sugeridos",
                "",
                self._markdown_list(suggested_tests),
            ]
        )

    def _markdown_list(self, values: list[str]) -> str:
        if not values:
            return "- Nenhum item identificado."
        return "\n".join(f"- {value}" for value in values)

    def _has_fragment(self, value: str, fragments: tuple[str, ...]) -> bool:
        normalized = value.lower()
        return any(fragment in normalized for fragment in fragments)
