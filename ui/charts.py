"""Pure, conservative table-to-chart inference; no generated JavaScript."""

from datetime import date
import math
import re


def infer_chart(columns, rows):
    default = {"type": "table"}
    if not columns or len(columns) < 2 or not rows:
        return default
    if any(not isinstance(row, (list, tuple)) or len(row) != len(columns) for row in rows):
        return default
    labels = [row[0] for row in rows]
    if not all(isinstance(value, str) and value for value in labels):
        return default
    date_like = [bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value)) for value in labels]
    if any(date_like):
        try:
            if not all(date_like) or any(date.fromisoformat(value).isoformat() != value for value in labels):
                return default
        except ValueError:
            return default
        kind = "line"
        order = sorted(range(len(rows)), key=lambda index: labels[index])
    else:
        kind = "bar"
        order = list(range(len(rows)))
    series = []
    for index in range(1, len(columns)):
        values = [row[index] for row in rows]
        if any(value is not None and type(value) not in (int, float) for value in values):
            continue
        cleaned = [value if value is not None and (type(value) is int or math.isfinite(value)) else None for value in values]
        if any(value is not None for value in cleaned):
            series.append({"name": str(columns[index]), "data": [cleaned[position] for position in order]})
    if not series:
        return default
    return {"type": kind, "x": str(columns[0]), "x_data": [labels[position] for position in order], "series": series}
