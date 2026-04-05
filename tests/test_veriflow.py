from goodshyt_operations.veriflow.service import VeriflowService


def test_parse_returns_canonical_linear_formula() -> None:
    service = VeriflowService()

    response = service.parse("Create an equation with m=3 and b=2")

    assert response.spec.task_type == "equation_creation"
    assert response.spec.parameters.m == 3
    assert response.spec.parameters.b == 2
    assert response.answer == "Created equation: y = m*x + b"
    assert response.validation.is_valid is True


def test_generate_data_returns_rows_and_validation() -> None:
    service = VeriflowService()

    response = service.generate_data("Generate data with m=3, b=2, x values 1, 2, 3")

    assert response.spec.task_type == "data_generation"
    assert response.rows == [[1.0, 5.0], [2.0, 8.0], [3.0, 11.0]]
    assert response.validation.is_valid is True
    assert "row verified: x=1, y=5" in response.validation.checks


def test_answer_returns_traceable_value_query() -> None:
    service = VeriflowService()

    response = service.answer("What is y when x=10 for y = 3*x + 2?")

    assert response.spec.task_type == "formula_question_answering"
    assert response.answer == "When x = 10, y = 32"
    assert response.validation.is_valid is True
    assert response.trace[-1].tool_name == "answer_linear_query"
