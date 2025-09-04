from flask import Flask, render_template, request, send_file
import psycopg2, io, os

app = Flask(__name__)

# Connect to PostgreSQL using DATABASE_URL from Render
def get_db_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"], sslmode="require")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    name = request.form['name']
    father_name = request.form['father_name']
    file = request.files['pdf']

    if file and file.filename.endswith('.pdf'):
        pdf_data = file.read()
        filename = file.filename

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS students (
                        id SERIAL PRIMARY KEY,
                        name TEXT,
                        father_name TEXT,
                        pdf_file BYTEA,
                        filename TEXT)''')

        cur.execute("INSERT INTO students (name, father_name, pdf_file, filename) VALUES (%s, %s, %s, %s)",
                    (name, father_name, psycopg2.Binary(pdf_data), filename))

        conn.commit()
        cur.close()
        conn.close()

        return render_template("success.html", name=name, father_name=father_name)

    return "❌ Please upload a valid PDF file."

@app.route('/view')
def view_files():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, father_name, filename FROM students")
    students = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("view.html", students=students)

@app.route('/download/<int:file_id>')
def download_file(file_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT pdf_file, filename FROM students WHERE id=%s", (file_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        pdf_data, filename = row
        return send_file(io.BytesIO(pdf_data), download_name=filename, as_attachment=False)
    return "❌ File not found"

if __name__ == '__main__':
    app.run(debug=True)
