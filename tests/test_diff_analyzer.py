from mcp_github_pr_reviewer.models import ChangedFile, PullRequest
from mcp_github_pr_reviewer.services.diff_analyzer import DiffAnalyzer


def test_analyze_flags_financial_and_missing_test_risks() -> None:
    pull_request = PullRequest(
        number=42,
        title="Update settlement flow",
        state="open",
        author="cosme",
        url="https://github.com/Cosmess/example/pull/42",
        base_branch="main",
        head_branch="feature/settlement",
    )
    files = [
        ChangedFile(
            filename="src/payments/settlement_service.py",
            status="modified",
            additions=80,
            deletions=10,
            changes=90,
        )
    ]

    analysis = DiffAnalyzer().analyze(pull_request, files)

    assert "PR #42 altera 1 arquivo" in analysis.summary
    assert "src/payments/settlement_service.py" in analysis.important_files
    assert any("fluxo financeiro" in risk for risk in analysis.risks)
    assert any("Nenhum arquivo de teste" in risk for risk in analysis.risks)
    assert any("cenários financeiros" in test for test in analysis.suggested_tests)
    assert "## Resumo técnico" in analysis.markdown_review


def test_analyze_handles_low_risk_pull_request() -> None:
    pull_request = PullRequest(
        number=7,
        title="Update documentation",
        state="open",
        author="cosme",
        url="https://github.com/Cosmess/example/pull/7",
        base_branch="main",
        head_branch="docs/readme",
    )
    files = [
        ChangedFile(
            filename="tests/test_readme_examples.py",
            status="added",
            additions=20,
            deletions=0,
            changes=20,
        )
    ]

    analysis = DiffAnalyzer().analyze(pull_request, files)

    assert analysis.risks == ["Nenhum risco evidente foi identificado pela análise heurística."]
    assert analysis.important_files == []
