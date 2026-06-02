from mcp_github_pr_reviewer.models import ErrorDetail, ToolResponse


def test_tool_response_success_shape() -> None:
    response = ToolResponse(ok=True, data={"value": 1}).model_dump()

    assert response["ok"] is True
    assert response["data"] == {"value": 1}
    assert response["error"] is None
    assert response["warnings"] == []


def test_tool_response_error_shape() -> None:
    response = ToolResponse(
        ok=False,
        error=ErrorDetail(code="repository_not_allowed", message="blocked"),
    ).model_dump()

    assert response["ok"] is False
    assert response["error"] == {
        "code": "repository_not_allowed",
        "message": "blocked",
    }
