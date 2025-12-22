import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from flask_fontawesome import FontAwesome


app = Flask(__name__)
fa = FontAwesome(app)

app.secret_key = 'mensagem_flash'

# Configurações do banco de dados MySQL
#app.config['MYSQL_HOST'] = 'localhost'
#app.config['MYSQL_USER'] = 'root'
#app.config['MYSQL_PASSWORD'] = 'bruno@974567'
#app.config['MYSQL_NAME'] = 'python_crud'
#app.config['MYSQL_DB'] = 'python_crud'
#app.config['MYSQL_PORT'] = 3306

import os

app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB')
app.config['MYSQL_PORT'] = int(os.environ.get('MYSQL_PORT', 3306))

app.secret_key = os.environ.get('SECRET_KEY')


mysql = MySQL(app)

# Página inicial
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM students")
    data = cur.fetchall()
    cur.close()
    return render_template('index.html', students=data)

# Inserir novo registro
@app.route('/inserir', methods=['POST'])
def inserir():
    if request.method == "POST":
        flash("Dados inseridos com sucesso!")

        nome = request.form['name']
        email = request.form['email']
        telefone = request.form['phone']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO students(name, email, phone) VALUES(%s, %s, %s)", (nome, email, telefone))
        mysql.connection.commit()
        return redirect(url_for('index'))

# Atualizar registro existente
@app.route('/atualizar', methods=['POST'])
def atualizar():
    if request.method == "POST":
        flash("Dados atualizados com sucesso!")

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
        return redirect(url_for('index'))

# Excluir registro
@app.route('/excluir/<string:id_dado>', methods=['POST','GET'])
def excluir(id_dado):
    flash("Dados excluídos com sucesso!")

    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM students WHERE id=%s", (id_dado,))
    mysql.connection.commit()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
