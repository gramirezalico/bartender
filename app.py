from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv()

app = Flask(__name__)


def normalize_unc_path(raw_path: str) -> str:
    cleaned = raw_path.strip()
    if cleaned.startswith("\\\\"):
        return cleaned
    if cleaned.startswith("//"):
        return "\\\\" + cleaned[2:].replace("/", "\\")
    return cleaned


def serialize_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def normalize_rows(payload_data: Any) -> list[dict[str, Any]]:
    if isinstance(payload_data, dict):
        return [payload_data]

    if isinstance(payload_data, list):
        rows: list[dict[str, Any]] = []
        for item in payload_data:
            if not isinstance(item, dict):
                raise ValueError("Si data es lista, todos los elementos deben ser objetos JSON")
            rows.append(item)
        return rows

    raise ValueError("El campo data debe ser un objeto JSON o una lista de objetos JSON")


@app.post("/csv")
def write_csv() -> tuple[Any, int]:
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"error": "Body JSON inválido"}), 400

    destination = body.get("destination")
    data = body.get("data")
    columns = body.get("columns")
    include_header = body.get("include_header", True)

    if not isinstance(destination, str) or not destination.strip():
        return jsonify({"error": "El campo 'destination' es obligatorio y debe ser string"}), 400

    if data is None:
        return jsonify({"error": "El campo 'data' es obligatorio"}), 400

    try:
        rows = normalize_rows(data)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if len(rows) == 0:
        return jsonify({"error": "El campo 'data' no puede estar vacío"}), 400

    if columns is not None:
        if not isinstance(columns, list) or not all(isinstance(c, str) and c for c in columns):
            return jsonify({"error": "'columns' debe ser una lista de strings no vacíos"}), 400
        fieldnames = columns
    else:
        discovered: list[str] = []
        seen: set[str] = set()
        for row in rows:
            for key in row.keys():
                if key not in seen:
                    seen.add(key)
                    discovered.append(key)
        fieldnames = discovered

    if len(fieldnames) == 0:
        return jsonify({"error": "No se detectaron columnas para generar el CSV"}), 400

    if not isinstance(include_header, bool):
        return jsonify({"error": "'include_header' debe ser boolean"}), 400

    unc_path = normalize_unc_path(destination)
    target_path = Path(unc_path)

    try:
        with target_path.open("w", newline="", encoding="utf-8-sig") as csv_file:
            writer = csv.writer(csv_file)

            if include_header:
                writer.writerow(fieldnames)

            for row in rows:
                writer.writerow([serialize_cell(row.get(column)) for column in fieldnames])

    except PermissionError:
        return jsonify({"error": f"Sin permisos para escribir en: {unc_path}"}), 403
    except OSError as exc:
        return jsonify({"error": f"No se pudo escribir el archivo: {exc}"}), 500

    return jsonify(
        {
            "ok": True,
            "path": unc_path,
            "rows_written": len(rows),
            "columns": fieldnames,
            "header_written": include_header,
        }
    ), 200



if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
