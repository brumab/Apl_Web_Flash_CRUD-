import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from flask_fontawesome import FontAwesome

app = Flask(__name__)
FontAwesome(app)

# =========================
# 🔐 Secret Key
# =========================
app.secret_key = os.environ.get("SECRET_KEY", "fallback_key")

# =========================
# 🗄️ MySQL Config (Aiven)
# =========================
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB')
app.config['MYSQL_PORT'] = int(os.environ.get('MYSQL_PORT', 3306))
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# =========================
# 🔒 Cria tabela se não existir
# (Flask 3 compatible)
# =========================
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

# Executa na inicialização da app
with app.app_context():
    create_table()

# =========================
# 📌 ROTAS
# =========================
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM students ORDER BY id DESC")
    data = cur.fetchall()
    cur.close()
    return render_template('index.html', students=data)

@app.route('/inserir', methods=['POST'])
def inserir():
    nome = request.form['name']
    email = request.form['email']
    telefone = request.form['phone']

    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO students (name, email, phone) VALUES (%s, %s, %s)",
        (nome, email, telefone)
    )
    mysql.connection.commit()
    cur.close()

    flash("Dados inseridos com sucesso!")
    return redirect(url_for('index'))

@app.route('/atualizar', methods=['POST'])
def atualizar():
    id_dado = request.form['id']
    nome = request.form['name']
    email = request.form['email']
    telefone = request.form['phone']

    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE students
        SET name=%s, email=%s, phone=%s
        WHERE id=%s
    """, (nome, email, telefone, id_dado))
    mysql.connection.commit()
    cur.close()

    flash("Dados atualizados com sucesso!")
    return redirect(url_for('index'))

@app.route('/excluir/<int:id_dado>')
def excluir(id_dado):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM students WHERE id=%s", (id_dado,))
    mysql.connection.commit()
    cur.close()

    flash("Dados excluídos com sucesso!")
    return redirect(url_for('index'))

# =========================
# 🚀 Local only
# =========================
if __name__ == "__main__":
    app.run(debug=True)
