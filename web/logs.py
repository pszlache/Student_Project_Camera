from flask import Blueprint, render_template_string
import sqlite3

logs_bp = Blueprint("logs", __name__)

DB_PATH = "logs/events.db"

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
    <td>{{ row[0] }}</td>
    <td>{{ row[1] }}</td>
    <td>{{ row[2] }}</td>
    <td>{{ row[3] }}</td>
    <td>
        {% if row[4] %}
            <a href="/{{ row[4] }}" target="_blank">View</a>
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
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT id, camera_name, start_time, end_time, snapshot_path
        FROM presence_events
        ORDER BY id DESC
        LIMIT 100
    """)

    rows = c.fetchall()
    conn.close()

    return render_template_string(HTML, rows=rows)