import pymysql
import os
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "flashcrud123")

# =========================
# Conexão MySQL - SEGURO (APENAS ENV)
# =========================
def get_db_connection():
    # Valida se todas as variáveis existem
    required = ['MYSQL_HOST', 'MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_DB']
    for var in required:
        if not os.getenv(var):
            raise ValueError(f"❌ Variável {var} não configurada no ambiente!")
    
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        cursorclass=pymysql.cursors.DictCursor,
        ssl={"ssl": {}},  # 🔒 SSL obrigatório Aiven
        connect_timeout=10
    )

# =========================
# Inicialização do banco
# =========================
db_initialized = False

def create_table():
    try:
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
        print("✅ Tabela students criada/verificada com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao criar tabela: {e}")
        raise

@app.before_request
def init_db():
    global db_initialized
    if not db_initialized:
        try:
            create_table()
            db_initialized = True
        except Exception as e:
            print("❌ Erro ao inicializar banco:", e)

# =========================
# Rotas
# =========================
@app.route("/test-db")
def test_db():
    """Testa a conexão com o banco"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT VERSION() as version, DATABASE() as db, USER() as user")
        result = cur.fetchone()
        cur.close()
        conn.close()
        return {
            "status": "success",
            "message": "✅ Conectado ao MySQL Aiven com sucesso!",
            "data": result
        }, 200
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ Erro MySQL: {str(e)}"
        }, 500

@app.route("/")
def index():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM students ORDER BY id DESC")
        students = cur.fetchall()
        cur.close()
        conn.close()
        return render_template("index.html", students=students)
    except Exception as e:
        flash(f"Erro ao carregar alunos: {str(e)}")
        return render_template("index.html", students=[])

@app.route("/inserir", methods=["POST"])
def inserir():
    try:
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
    except Exception as e:
        flash(f"Erro ao cadastrar: {str(e)}")
    
    return redirect(url_for("index"))

@app.route("/atualizar", methods=["POST"])
def atualizar():
    try:
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
    except Exception as e:
        flash(f"Erro ao atualizar: {str(e)}")
    
    return redirect(url_for("index"))

@app.route("/excluir/<int:id_dado>", methods=["POST"])
def excluir(id_dado):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM students WHERE id=%s", (id_dado,))
        conn.commit()
        cur.close()
        conn.close()
        flash("Aluno excluído com sucesso!")
    except Exception as e:
        flash(f"Erro ao excluir: {str(e)}")
    
    return redirect(url_for("index"))

@app.route("/health")
def health():
    """Health check para o Render"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return {"status": "ok", "database": "connected"}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.route("/debug-env")
def debug_env():
    """DEBUG: Mostra quais variáveis estão configuradas (SEM OS VALORES!)"""
    vars_to_check = ['MYSQL_HOST', 'MYSQL_USER', 'MYSQL_PASSWORD', 'MYSQL_DB', 'MYSQL_PORT']
    return {
        var: "✅ Configurada" if os.getenv(var) else "❌ NÃO CONFIGURADA"
        for var in vars_to_check
    }

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
