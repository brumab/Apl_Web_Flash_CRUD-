import os
from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB')
app.config['MYSQL_PORT'] = int(os.environ.get('MYSQL_PORT', 3306))
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_SSL'] = {'ssl-mode': 'REQUIRED'}

mysql = MySQL(app)


# =========================
# 🔒 Inicialização segura do banco (Flask 3.x)
# =========================
db_initialized = False

def create_table():
    cur = mysql.connection.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL,
            phone VARCHAR(20) NOT NULL
        )
    """)
    mysql.connection.commit()
    cur.close()
    print("Tabela students pronta")

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
# 📌 ROTAS
# =========================
@app.route("/test-db")
def test_db():
    try:
        conn = mysql.connection
        return "✅ Conectado ao MySQL com sucesso"
    except Exception as e:
        return f"❌ Erro MySQL: {e}"

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM students ORDER BY id DESC")
    students = cur.fetchall()
    cur.close()
    return render_template('index.html', students=students)

@app.route('/inserir', methods=['POST'])
def inserir():
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO students (name, email, phone) VALUES (%s, %s, %s)",
        (request.form['name'], request.form['email'], request.form['phone'])
    )
    mysql.connection.commit()
    cur.close()
    flash("Aluno cadastrado com sucesso!")
    return redirect(url_for('index'))

@app.route('/atualizar', methods=['POST'])
def atualizar():
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE students
        SET name=%s, email=%s, phone=%s
        WHERE id=%s
    """, (
        request.form['name'],
        request.form['email'],
        request.form['phone'],
        request.form['id']
    ))
    mysql.connection.commit()
    cur.close()
    flash("Aluno atualizado com sucesso!")
    return redirect(url_for('index'))

@app.route('/excluir/<int:id_dado>', methods=['POST'])
def excluir(id_dado):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM students WHERE id=%s", (id_dado,))
    mysql.connection.commit()
    cur.close()
    flash("Aluno excluído com sucesso!")
    return redirect(url_for('index'))

# =========================
# 🚀 Local only
# =========================
if __name__ == "__main__":
    app.run(debug=True)
