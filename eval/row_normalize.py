"""Stable JSON round-trip normalization for offline reference rows."""

import json
from agent.mcp_server import json_value


def normalize_rows(rows):
    """Normalize dates/decimals using the existing serializer, then round-trip JSON."""
    return json.loads(json.dumps([[json_value(value) for value in row] for row in rows],
                                 ensure_ascii=False, allow_nan=False))
