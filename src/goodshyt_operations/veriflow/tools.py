from __future__ import annotations

from .models import LinearModelParameters


def format_formula(parameters: LinearModelParameters) -> str:
    sign = "+" if parameters.b >= 0 else "-"
    return f"y = {parameters.m:g}*x {sign} {abs(parameters.b):g}"


def generate_linear_rows(
    parameters: LinearModelParameters,
    x_values: list[float],
) -> tuple[list[list[float]], list[str]]:
    rows: list[list[float]] = []
    steps = [
        f"Use the linear model {format_formula(parameters)}.",
        "For each x value, compute y = m*x + b.",
    ]
    for value in x_values:
        y_value = parameters.m * value + parameters.b
        rows.append([float(value), float(y_value)])
        steps.append(f"x = {value:g} -> y = {parameters.m:g}*{value:g} + {parameters.b:g} = {y_value:g}")
    return rows, steps


def answer_linear_query(
    parameters: LinearModelParameters,
    x_value: float,
) -> tuple[str, list[str]]:
    y_value = parameters.m * x_value + parameters.b
    steps = [
        f"Use the linear model {format_formula(parameters)}.",
        f"Substitute x = {x_value:g} into y = m*x + b.",
        f"Compute y = {parameters.m:g}*{x_value:g} + {parameters.b:g} = {y_value:g}.",
    ]
    answer = f"When x = {x_value:g}, y = {y_value:g}"
    return answer, steps
