from flask import Flask
import psycopg2
import os

app = Flask(__name__)

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

@app.route("/")
def dashboard():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT ON (url)
               url,
               status,
               response_ms,
               checked_at
        FROM checks
        ORDER BY url, checked_at DESC
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    html = """
    <html>
    <head>
      <title>URL Watcher</title>
      <style>
      body {
        font-family: Arial;
        margin: 40px;
      }
      table {
        border-collapse: collapse;
      }
      th, td {
        border: 1px solid #ddd;
        padding: 10px;
      }
      .UP {
        color: green;
        font-weight: bold;
      }
      .DOWN {
        color: red;
        font-weight: bold;
      }
      </style>
    </head>
    <body>
    <h1>URL Watcher</h1>

    <table>
      <tr>
        <th>URL</th>
        <th>Status</th>
        <th>Response Time</th>
      </tr>
    """

    for row in rows:
        html += f"""
        <tr>
          <td>{row[0]}</td>
          <td class='{row[1]}'>{row[1]}</td>
          <td>{row[2]} ms</td>
        </tr>
        """

    html += """
    </table>
    </body>
    </html>
    """

    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)