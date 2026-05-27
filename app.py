import pymysql
import os
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "flashcrud123"

# =========================
# Conexão MySQL (Aiven)
# =========================
def get_db_connection():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        cursorclass=pymysql.cursors.DictCursor,
        ssl={"ssl": {}}  # 🔒 SSL obrigatório Aiven
    )


# =========================
# Inicialização do banco
# =========================
db_initialized = False

def create_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL,
            phone VARCHAR(20) NOT NULL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.before_request
def init_db():
    global db_initialized
    if not db_initialized:
        try:
            create_table()
            db_initialized = True
        except Exception as e:
            print("Erro ao inicializar banco:", e)

# =========================
# Rotas
# =========================
@app.route("/test-db")
def test_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return "✅ Conectado ao MySQL Aiven com sucesso"
    except Exception:
        app.logger.exception("Erro ao testar conexão com MySQL")
        return "❌ Erro interno ao conectar ao banco de dados.", 500

@app.route("/")
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM students ORDER BY id DESC")
    students = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", students=students)

@app.route("/inserir", methods=["POST"])
def inserir():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO students (name, email, phone) VALUES (%s, %s, %s)",
        (request.form["name"], request.form["email"], request.form["phone"])
    )
    conn.commit()
    cur.close()
    conn.close()
    flash("Aluno cadastrado com sucesso!")
    return redirect(url_for("index"))

@app.route("/atualizar", methods=["POST"])
def atualizar():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE students
        SET name=%s, email=%s, phone=%s
        WHERE id=%s
    """, (
        request.form["name"],
        request.form["email"],
        request.form["phone"],
        request.form["id"]
    ))
    conn.commit()
    cur.close()
    conn.close()
    flash("Aluno atualizado com sucesso!")
    return redirect(url_for("index"))

@app.route("/excluir/<int:id_dado>", methods=["POST"])
def excluir(id_dado):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE id=%s", (id_dado,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Aluno excluído com sucesso!")
    return redirect(url_for("index"))
