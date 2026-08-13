import os

import pyodbc
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for


load_dotenv()

app = Flask(__name__)

app.secret_key = "123456"

def conectar_banco():
    return pyodbc.connect(
        f"DRIVER={{{os.getenv('DB_DRIVER')}}};"
        f"SERVER={os.getenv('DB_SERVER')};"
        f"DATABASE={os.getenv('DB_DATABASE')};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )

@app.route("/")
def pagina_cadastro():

    pesquisa = request.args.get("pesquisa", "").strip()

    conexao = conectar_banco()
    cursor = conexao.cursor()

    # Dashboard

    cursor.execute("SELECT COUNT(*) FROM ALUNO")
    total_alunos = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM ALUNO
        WHERE SEXO = 'M'
        """
    )
    total_homens = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM ALUNO
        WHERE SEXO = 'F'
        """
    )
    total_mulheres = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT AVG(DATEDIFF(YEAR, NASCIMENTO, GETDATE()))
        FROM ALUNO
        """
    )
    idade_media = int(cursor.fetchone()[0])


    if pesquisa:

        cursor.execute(
            """
            SELECT IDALUNO, NOME, SEXO, NASCIMENTO, EMAIL
            FROM ALUNO
            WHERE NOME LIKE ?
            ORDER BY IDALUNO DESC
            """,
            f"%{pesquisa}%"
        )

    else:

        cursor.execute(
            """
            SELECT IDALUNO, NOME, SEXO, NASCIMENTO, EMAIL
            FROM ALUNO
            ORDER BY IDALUNO DESC
            """
        )

    alunos = cursor.fetchall()

    conexao.close()

    return render_template(
        "cadastro.html",
        alunos=alunos,
        pesquisa=pesquisa,
        total_alunos=total_alunos,
        total_homens=total_homens,
        total_mulheres=total_mulheres,
        idade_media=idade_media
    )

@app.route("/editar/<int:id_aluno>")
def editar_aluno(id_aluno):
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(
        """
        SELECT IDALUNO, NOME, SEXO, NASCIMENTO, EMAIL
        FROM ALUNO
        WHERE IDALUNO = ?
        """,
        id_aluno,
    )

    aluno = cursor.fetchone()

    cursor.execute(
        """
        SELECT IDALUNO, NOME, SEXO, NASCIMENTO, EMAIL
        FROM ALUNO
        ORDER BY IDALUNO DESC
        """
    )

    alunos = cursor.fetchall()

    conexao.close()

    return render_template(
        "cadastro.html",
        aluno_edicao=aluno,
        alunos=alunos,
    )

@app.route("/salvar", methods=["POST"])
def salvar_aluno():
    nome = request.form.get("nome", "").strip()
    sexo = request.form.get("sexo", "").strip()
    nascimento = request.form.get("nascimento", "").strip()
    email = request.form.get("email", "").strip()

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(
        """
        INSERT INTO ALUNO (NOME, SEXO, NASCIMENTO, EMAIL)
        VALUES (?, ?, ?, ?)
        """,
        nome,
        sexo,
        nascimento,
        email or None,
    )


    conexao.commit()
    conexao.close()

    return redirect(url_for("pagina_cadastro"))

@app.route("/atualizar/<int:id_aluno>", methods=["POST"])
def atualizar_aluno(id_aluno):
    nome = request.form.get("nome", "").strip()
    sexo = request.form.get("sexo", "").strip()
    nascimento = request.form.get("nascimento", "").strip()
    email = request.form.get("email", "").strip()

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(
        """
        UPDATE ALUNO
        SET
            NOME = ?,
            SEXO = ?,
            NASCIMENTO = ?,
            EMAIL = ?
        WHERE IDALUNO = ?
        """,
        nome,
        sexo,
        nascimento,
        email or None,
        id_aluno,
    )

    conexao.commit()
    conexao.close()

    return redirect(url_for("pagina_cadastro"))

@app.route("/excluir/<int:id_aluno>", methods=["POST"])
def excluir_aluno(id_aluno):

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute(
        """
        DELETE FROM ALUNO
        
        WHERE IDALUNO = ?
        """,
        id_aluno,
    )

    conexao.commit()
    conexao.close()

    return redirect(url_for("pagina_cadastro"))



if __name__ == "__main__":
    app.run(debug=True)