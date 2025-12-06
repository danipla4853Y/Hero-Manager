from flask import Flask, render_template, request, redirect, session, url_for, flash,get_flashed_messages, jsonify
import mysql.connector
from flask_session import Session

app = Flask(__name__)

app.secret_key = "67"

db_config = {
    'host':'localhost',
    'user': 'root',
    'password':'',
    'database': 'banco'
}


@app.route("/")
def main():
    return redirect(url_for("cadastro"))
    


@app.route('/cadastro',methods=['GET','POST'])
def cadastro():
    if request.method == 'POST':    
        
        nome = request.form['Nome_cadastro']
        email = request.form['Email_cadastro']
        cpf = request.form['Cpf_cadastro']
        senha = request.form['Senha_cadastro']
        planeta = request.form['Planeta_cadastro']
        logado = False
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuarios  WHERE nome = %s OR email = %s', (nome,email))
        if cursor.fetchone():

            flash("Nome de usuário ou email ja cadastrado.","erro")
            return redirect(url_for('cadastro'))
        logado = True
        cursor.execute("INSERT INTO usuarios (nome,email,cpf,senha,planeta,logado) VALUES (%s,%s,%s,%s,%s,%s) ",(nome,email,cpf,senha,planeta,logado))
        

        
        conn.commit()
        cursor.close()
        conn.close()

        flash("Cadastro realizado com sucesso! Voce ja pode fazer login.", "sucesso.")
        return redirect(url_for('login'))

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("select imagem_url from herois")
    imagens = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return render_template("cadastro.html", imagens=imagens)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        email = request.form['Email_login']
        senha = request.form['Senha_login']

        cursor.execute("SELECT id, nome, email, planeta FROM usuarios WHERE email = %s AND senha = %s",
                       (email, senha))
        usuario = cursor.fetchone()

        if usuario:
            # Salva na sessão
            session['usuario'] = {
                "id": usuario[0],
                "nome": usuario[1],
                "email": usuario[2],
                "planeta": usuario[3]
            }

            cursor.close()
            conn.close()

            return redirect(url_for("home"))
        else:
            flash("Email ou senha incorretos!", "erro")

        cursor.close()
        conn.close()

    return render_template("login.html")
@app.route('/home')
def home():
    return render_template("home.html")


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'usuario' not in session:
        flash("Você precisa estar logado para acessar o perfil.", "erro")
        return redirect(url_for('login'))

    user_id = session['usuario']['id']

    conn = _get_conn()
    cursor = conn.cursor()

    # Se o usuário clicou em "Salvar"
    if request.method == 'POST':
        novo_nome = request.form['nome']
        novo_email = request.form['email']
        novo_planeta = request.form['planeta']
        nova_senha = request.form['senha']

        cursor.execute("""
            UPDATE usuarios 
            SET nome=%s, email=%s, planeta=%s, senha=%s
            WHERE id=%s
        """, (novo_nome, novo_email, novo_planeta, nova_senha, user_id))
        conn.commit()

        # Atualiza também na sessão
        session['usuario']['nome'] = novo_nome
        session['usuario']['email'] = novo_email
        session['usuario']['planeta'] = novo_planeta

        flash("Dados atualizados com sucesso!", "sucesso")

    # Buscar dados atualizados do usuário
    cursor.execute("SELECT id, nome, email, cpf, senha, planeta FROM usuarios WHERE id=%s", (user_id,))
    usuario = cursor.fetchone()

    # Buscar equipe do usuário (máx 5)
    cursor.execute("""
        SELECT h.* 
        FROM herois h
        JOIN herois_equipe he ON h.id = he.heroi_id
        JOIN equipes e ON e.id = he.equipe_id
        WHERE e.user_id = %s
        LIMIT 5
    """, (user_id,))
    equipe = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("perfil.html", usuario=usuario, equipe=equipe)

def _get_conn():
    return mysql.connector.connect(**db_config)

def _fetch_herois_by_ids(ids):
    """
    Recebe uma lista de ids (int) e retorna as linhas correspondentes da tabela herois.
    Retorna lista vazia se ids for vazio.
    Mantém a ordem dos ids passada (caso necessário, ordena em Python).
    """
    if not ids:
        return []

    conn = _get_conn()
    cursor = conn.cursor()
    placeholders = ','.join(['%s'] * len(ids))
    cursor.execute(f"SELECT * FROM herois WHERE id IN ({placeholders})", tuple(ids))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # Mantém a ordem conforme lista de ids
    rows_by_id = {row[0]: row for row in rows}
    ordered = [rows_by_id[i] for i in ids if i in rows_by_id]
    return ordered

@app.route('/herois')
def herois():
    if 'usuario' not in session:
        flash("Você precisa estar logado.", "erro")
        return redirect(url_for('login'))

    user_id = session['usuario']['id']

    conn = _get_conn()
    cursor = conn.cursor()

    # Todos os heróis disponíveis
    cursor.execute("SELECT * FROM herois")
    all_herois = cursor.fetchall()

    # Equipe do usuário (máx 5)
    cursor.execute("""
        SELECT h.* 
        FROM herois h
        JOIN herois_equipe he ON h.id = he.heroi_id
        JOIN equipes e ON e.id = he.equipe_id
        WHERE e.user_id = %s
        LIMIT 5
    """, (user_id,))
    equipe = cursor.fetchall()


    cursor.close()
    conn.close()

    return render_template("herois.html", herois=all_herois, equipe=equipe)

@app.route('/buscar_herois')
def buscar_herois():
    q = request.args.get('q', '').strip()
    tipo = request.args.get('tipo', 'nome')
    session.setdefault('equipe', [])


    conn = _get_conn()
    cursor = conn.cursor()

    if tipo == 'id':
        try:
            hid = int(q)
            cursor.execute("SELECT * FROM herois WHERE id = %s", (hid,))
        except ValueError:
            cursor.execute("SELECT * FROM herois WHERE 1=0")  # nenhum resultado
    else:
        like = f"%{q}%"
        cursor.execute("SELECT * FROM herois WHERE nome LIKE %s OR classe LIKE %s", (like, like))

    resultados = cursor.fetchall()
    cursor.close()
    conn.close()

    equipe = _fetch_herois_by_ids(session.get('equipe', []))

    return render_template("herois.html", herois=resultados, equipe=equipe)


@app.route('/adicionar_equipe', methods=['POST'])
def adicionar_equipe():
    if 'usuario' not in session:
        return jsonify({"success": False, "message": "Você precisa estar logado."}), 401

    user_id = session['usuario']['id']
    hid = request.form.get('heroi_id')
    if not hid:
        return jsonify({"success": False, "message": "ID do herói não fornecido."}), 400

    hid_int = int(hid)

    conn = _get_conn()
    cursor = conn.cursor()

    # Verifica se já existe equipe para o usuário
    cursor.execute("SELECT id FROM equipes WHERE user_id = %s", (user_id,))
    equipe = cursor.fetchone()

    if not equipe:
        # cria equipe automaticamente
        cursor.execute("INSERT INTO equipes (user_id, nome) VALUES (%s, %s)", (user_id, "Equipe Principal"))
        conn.commit()
        equipe_id = cursor.lastrowid
    else:
        equipe_id = equipe[0]

    # Verifica se o herói já está na equipe
    cursor.execute("SELECT COUNT(*) FROM herois_equipe WHERE equipe_id = %s AND heroi_id = %s", (equipe_id, hid_int))
    hero_exists = cursor.fetchone()[0]

    if hero_exists:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "message": "Este herói já está na sua equipe!"}), 400

    # Conta quantos heróis já estão na equipe
    cursor.execute("SELECT COUNT(*) FROM herois_equipe WHERE equipe_id = %s", (equipe_id,))
    qtd = cursor.fetchone()[0]

    if qtd >= 5:
        cursor.close()
        conn.close()
        return jsonify({"success": False, "message": "Equipe já tem 5 heróis!"}), 400

    cursor.execute("INSERT INTO herois_equipe (equipe_id, heroi_id) VALUES (%s, %s)", (equipe_id, hid_int))
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({"success": True, "message": "Herói adicionado à equipe."}), 200



@app.route('/remover_heroi', methods=['POST'])
def remover_heroi():
    if 'usuario' not in session:
        flash("Você precisa estar logado.", "erro")
        return redirect(url_for('login'))

    user_id = session['usuario']['id']
    heroi_id = int(request.form.get('heroi_id'))

    conn = _get_conn()
    cursor = conn.cursor()

    # Descobre qual equipe pertence ao usuário
    cursor.execute("SELECT id FROM equipes WHERE user_id = %s", (user_id,))
    equipe = cursor.fetchone()

    if equipe:
        equipe_id = equipe[0]
        # Remove apenas da relação equipe-herói
        cursor.execute("DELETE FROM herois_equipe WHERE equipe_id = %s AND heroi_id = %s", (equipe_id, heroi_id))
        conn.commit()
        flash("Herói removido da equipe.", "sucesso")
    else:
        flash("Nenhuma equipe encontrada para este usuário.", "erro")

    cursor.close()
    conn.close()
    return redirect(url_for('herois'))

if __name__ == "__main__":
    app.run(debug=True)



#https://docs.google.com/document/d/1T9XJlr3Bm6NibDDFn8jUrLRKUZYKGLli/edit