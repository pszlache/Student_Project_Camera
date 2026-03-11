from flask import Blueprint, render_template_string
from src.database.db import _get_connection
import sqlite3

logs_bp = Blueprint("logs", __name__)

HTML = """
<!doctype html>
<html>
<head>
    <title>Presence Logs</title>
    <style>
        body { font-family: Arial; background:#111; color:#eee; }
        table { border-collapse: collapse; width: 100%; }
        th, td { padding: 8px; border-bottom: 1px solid #444; }
        th { background:#222; }
        a { color:#4caf50; text-decoration:none; }
    </style>
</head>
<body>
<h1>Presence Logs</h1>
<table>
<tr>
    <th>ID</th>
    <th>Camera</th>
    <th>Start</th>
    <th>End</th>
    <th>Snapshot</th>
</tr>
{% for row in rows %}
<tr>
    <td>{{ row["id"] }}</td>
    <td>{{ row["camera_name"] }}</td>
    <td>{{ row["start_time"] }}</td>
    <td>{{ row["end_time"] }}</td>
    <td>
        {% if row["snapshot_path"] %}
            <a href="/{{ row["snapshot_path"] }}" target="_blank">View</a>
        {% else %}
            —
        {% endif %}
    </td>
</tr>
{% endfor %}
</table>
</body>
</html>
"""

@logs_bp.route("/logs")
def show_logs():

    conn = _get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, camera_name, start_time, end_time, snapshot_path
        FROM presence_events
        ORDER BY id DESC
        LIMIT 100
    """)

    rows = cursor.fetchall()
    conn.close()

    return render_template_string(HTML, rows=rows)