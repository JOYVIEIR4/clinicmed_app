from flask import Flask, render_template, request, redirect, url_for, flash, session
import pymysql.cursors
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

DB_CONFIG = {
    'host': os.environ.get('DB_HOST'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'db': os.environ.get('DB_NAME', 'clinicmed_db'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    try:
        connection = pymysql.connect(**DB_CONFIG)
        return connection
    except pymysql.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        flash('Erro ao conectar com o banco de dados. Tente novamente mais tarde.', 'error')
        return None
    
#////////////////////////// INICIO //////////////////////////////////////////////////#

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')

        # LOGIN SIMPLIFICADO (fixo)
        if usuario == 'julia.martins' and senha == '1234abc':
            session['logado'] = True
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha incorretos!', 'danger')

    return render_template('inicio.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logado'):
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))



#///////////////////////////// PACIENTES ///////////////////////////////////////////#
@app.route('/pacientes')
def listar_pacientes():
    if not session.get('logado'):
        return redirect(url_for('login'))

    lista = []  

    conn = get_db_connection()
    if conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Paciente")
            lista = cursor.fetchall()
        conn.close()

    return render_template('pacientes.html', paciente=lista)


@app.route('/pacientes/add', methods=('GET', 'POST'))
def adicionar_paciente():
    if not session.get('logado'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        data = request.form.get('data_nascimento')
        contato = request.form.get('contato')

        if not nome:
            flash('O nome é obrigatório.', 'error')
            return redirect(url_for('add_paciente'))

        conn = get_db_connection()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Paciente (nome, data_nascimento, contato)
                    VALUES (%s, %s, %s)
                """, (nome, data, contato))
                conn.commit()
            conn.close()
            flash('Paciente cadastrado com sucesso!')
            return redirect(url_for('listar_pacientes'))

    return render_template('add_paciente.html')


@app.route('/pacientes/edit/<int:id>', methods=('GET', 'POST'))
def edit_paciente(id):
    if not session.get('logado'):
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    paciente = None

    if conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Paciente WHERE id_paciente = %s", (id,))
            paciente = cursor.fetchone()

        if not paciente:
            flash('Paciente não encontrado.', 'error')
            conn.close()
            return redirect(url_for('listar_pacientes'))

        if request.method == 'POST':
            nome = request.form.get('nome')
            data_nascimento = request.form.get('data_nascimento')
            contato = request.form.get('contato')

            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE Paciente
                    SET nome = %s, data_nascimento = %s, contato = %s
                    WHERE id_paciente = %s
                """, (nome, data_nascimento, contato, id))
                conn.commit()
            conn.close()
            flash('Paciente atualizado com sucesso!')
            return redirect(url_for('listar_pacientes'))

        conn.close()

    return render_template('edit_paciente.html', paciente=paciente)


@app.route('/pacientes/delete/<int:id>', methods=('POST',))
def deletar_paciente(id):
    if not session.get('logado'):
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM Paciente WHERE id_paciente = %s", (id,))
                conn.commit()
            flash('Paciente deletado com sucesso!', 'success')
        except Exception as e:
            flash(f"Erro ao excluir paciente: {e}", "error")
        finally:
            conn.close()

    return redirect(url_for('listar_pacientes'))
    

    ####################### PROFISSIONAL ###########################

@app.route('/profissionais')
def listar_profissional():
    if not session.get('logado'):
        return redirect(url_for('login'))

    lista = []  

    conn = get_db_connection()
    if conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Profissional")
            lista = cursor.fetchall()
        conn.close()

    return render_template('profissional.html', profissional=lista)


@app.route('/profissionais/add', methods=('GET', 'POST'))
def adicionar_profissional():
    if not session.get('logado'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome = request.form.get('nome').strip()

        if not nome:
            flash('O nome é obrigatório.', 'error')
            return redirect(url_for('adicionar_profissional'))

        conn = get_db_connection()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Profissional (nome)
                    VALUES (%s)
                """, (nome,))
                conn.commit()
            conn.close()
            flash('Profissional cadastrado com sucesso!')
            return redirect(url_for('listar_profissional'))

    return render_template('add_profissional.html')


@app.route('/profissionais/edit/<int:id>', methods=('GET', 'POST'))
def edit_profissional(id):
    if not session.get('logado'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    profissional = None

    if conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Profissional WHERE id_profissional = %s", (id,))
            profissional = cursor.fetchone()

        if not profissional:
            flash('Profissional não encontrado.', 'error')
            conn.close()
            return redirect(url_for('listar_profissional'))

        if request.method == 'POST':
            nome = request.form.get('nome')

            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE Profissional
                    SET nome = %s
                    WHERE id_profissional = %s
                """, (nome, id))
                conn.commit()
            conn.close()
            flash('Profissional atualizado com sucesso!')
            return redirect(url_for('listar_profissional'))

        conn.close()

    return render_template('edit_profissional.html', profissional=profissional)


@app.route('/profissionais/delete/<int:id>', methods=('POST',))
def deletar_profissional(id):
    if not session.get('logado'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM Profissional WHERE id_profissional = %s", (id,))
                conn.commit()
            flash('Profissional deletado com sucesso!', 'success')
        except Exception as e:
            flash(f"Erro ao excluir profissional: {e}", "error")
        finally:
            conn.close()

    return redirect(url_for('listar_profissional'))

#//////////////////////////////////////////// MEDICAMENTOS //////////////////////////////#

@app.route('/medicamentos')
def listar_medicamento():
    if not session.get('logado'):
        return redirect(url_for('login'))

    lista = []  

    conn = get_db_connection()
    if conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Medicamento")
            lista = cursor.fetchall()
        conn.close()

    return render_template('medicamento.html', medicamento=lista)


@app.route('/medicamento/add', methods=('GET', 'POST'))
def adicionar_medicamento():
    if not session.get('logado'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome = request.form.get('nome').strip()
        via = request.form.get('via_administracao')
        descricao = request.form.get('desc_medicamento')

        if not nome:
            flash('O nome é obrigatório.', 'error')
            return redirect(url_for('adicionar_medicamento'))

        conn = get_db_connection()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Medicamento (nome, via_administracao, desc_medicamento )
                    VALUES (%s, %s, %s)
                """, (nome, via, descricao))
                conn.commit()
            conn.close()
            flash('Medicamento cadastrado com sucesso!')
            return redirect(url_for('listar_medicamento'))

    return render_template('add_medicamento.html')


@app.route('/medicamento/edit/<int:id>', methods=('GET', 'POST'))
def edit_medicamento(id):
    if not session.get('logado'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    medicamento = None

    if conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT nome, via_administracao, desc_medicamento FROM Medicamento WHERE id_medicamento = %s", (id,))
            medicamento = cursor.fetchone()

        if not medicamento:
            flash('Medicamento não encontrado.', 'error')
            conn.close()
            return redirect(url_for('listar_medicamento'))

        if request.method == 'POST':
            nome = request.form.get('nome')
            via = request.form.get('via_administracao')
            descricao = request.form.get('desc_medicamento')

            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE Medicamento
                    SET nome = %s, via_administracao = %s, desc_medicamento = %s
                    WHERE id_medicamento = %s
                """, (nome, via, descricao, id))
                conn.commit()
            conn.close()
            flash('Medicamento atualizado com sucesso!')
            return redirect(url_for('listar_medicamento'))

        conn.close()

    return render_template('edit_medicamento.html', medicamento=medicamento)


@app.route('/medicamento/delete/<int:id>', methods=('POST',))
def deletar_medicamento(id):
    if not session.get('logado'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM Medicamento WHERE id_medicamento = %s", (id,))
                conn.commit()
            flash('Medicamento deletado com sucesso!', 'success')
        except Exception as e:
            flash(f"Erro ao excluir medicamento: {e}", "error")
        finally:
            conn.close()

    return redirect(url_for('listar_medicamento'))

#//////////////////////      PRESCRICAO        //////////////////////////////////////////#

@app.route('/prescricao')
def listar_prescricao():
    if not session.get('logado'):
        return redirect(url_for('login'))

    lista = []  

    conn = get_db_connection()
    if conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                p.id_prescricao,
                pac.nome AS nome,
                prof.nome_profissional AS nome_profissional,
                med.nome AS medicamento_nome,
                p.dosagem_prescricao,
                p.dt_inicio_prescricao,
                p.dt_fim_prescricao,
                p.observacoes
        FROM Prescricao p
        JOIN Paciente pac ON pac.id_paciente = p.id_paciente
        JOIN Profissional prof ON prof.id_profissional = p.id_profissional
        JOIN Medicamento med ON med.id_medicamento = p.id_medicamento;
    """)
    lista = cursor.fetchall()


    return render_template('prescricao.html', prescricao=lista)


@app.route('/prescricao/add', methods=('GET', 'POST'))
def adicionar_prescricao():
    if not session.get('logado'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        paciente = request.form.get('id_paciente')
        profissional = request.form.get('id_profissional')
        medicamento = request.form.get('id_medicamento')
        posologia = request.form.get('dosagem_prescricao')
        inicio_prescricao = request.form.get('dt_inicio_prescricao')
        fim_prescricao = request.form.get('dt_fim_prescricao')
        observacao = request.form.get('observacoes')

        if not posologia:
            flash('A posologia é obrigatório.', 'error')
            return redirect(url_for('adicionar_prescricao'))

        conn = get_db_connection()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO prescricao (id_paciente, id_profissional, id_medicamento, dosagem_prescricao, dt_inicio_prescricao, dt_fim_prescricao, observacoes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (paciente, profissional, medicamento, posologia, inicio_prescricao, fim_prescricao, observacao))
                conn.commit()
            conn.close()
            flash('Prescrição cadastrada com sucesso!')
            return redirect(url_for('listar_prescricao'))

    return render_template('add_prescricao.html')


@app.route('/prescricao/edit/<int:id>', methods=('GET', 'POST'))
def edit_prescricao(id):
    if not session.get('logado'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    prescricao = None

    if conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id_prescricao, id_paciente, id_profissional, id_medicamento, dosagem_prescricao, dt_inicio_prescricao,               dt_fim_prescricao, observacoes 
                FROM Prescricao 
                WHERE id_prescricao = %s""", (id,))
            prescricao = cursor.fetchone()

        if not prescricao:
            flash('Prescrição não encontrada.', 'error')
            conn.close()
            return redirect(url_for('listar_prescricao'))

        if request.method == 'POST':
            prescricao = request.form.get('id_prescricao')
            paciente = request.form.get('id_paciente')
            profissional = request.form.get('id_profissional')
            medicamento = request.form.get('id_medicamento')
            posologia = request.form.get('dosagem_prescricao')
            inicio_prescricao = request.form.get('dt_inicio_prescricao')
            fim_prescricao = request.form.get('dt_fim_prescricao')
            observacao = request.form.get('observacoes')    

            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE Prescricao
                    SET id_prescricao = %s, 
                        id_paciente = %s, 
                        id_profissional = %s, 
                        id_medicamento = %s, 
                        dosagem_prescricao = %s, 
                        dt_inicio_prescricao = %s, 
                        dt_fim_prescricao = %s, 
                        observacoes = %s
                    WHERE id_prescricao = %s
                """, (prescricao, paciente, profissional, medicamento, posologia, inicio_prescricao, fim_prescricao, observacao, id))
                conn.commit()

            conn.close()
            flash('prescrição atualizada com sucesso!')
            return redirect(url_for('listar_prescricao'))

        conn.close()

    return render_template('edit_prescricao.html', prescricao=prescricao)


@app.route('/prescricao/delete/<int:id>', methods=('POST',))
def deletar_prescricao(id):
    if not session.get('logado'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM Prescricao WHERE id_prescricao = %s", (id,))
                conn.commit()
            flash('Prescrição deletada com sucesso!', 'success')
        except Exception as e:
            flash(f"Erro ao excluir prescrição: {e}", "error")
        finally:
            conn.close()

    return redirect(url_for('listar_prescricao'))

#//////////////////////////////// ADMINISTRACAO //////////////////////////////#

@app.route('/administracao/add/<int:id>', methods=['GET', 'POST'])
def add_administracao(id):
    if not session.get('logado'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        dose_aplicada = request.form.get('dose_aplicada')
        data_aplicacao = request.form.get('data_aplicacao')

        cursor.execute("""
            INSERT INTO administracao (id_prescricao, dose_aplicada, data_aplicacao)
            VALUES (%s, %s, %s)
        """, (id, dose_aplicada, data_aplicacao))

        conn.commit()

        cursor.close()
        conn.close()

        flash("Administração registrada com sucesso!", "success")
        return redirect(url_for('listar_prescricao'))

    # GET — pegar dados da prescrição
    cursor.execute("""
        SELECT 
            p.id_prescricao, 
            pac.nome AS paciente, 
            m.nome AS medicamento
        FROM prescricao p
        JOIN paciente pac ON pac.id_paciente = p.id_paciente
        JOIN medicamento m ON m.id_medicamento = p.id_medicamento
        WHERE p.id_prescricao = %s
    """, (id,))

    prescricao = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('add_administracao.html', prescricao=prescricao)

@app.route('/administracao/historico/<int:id_prescricao>')
def historico_administracao(id_prescricao):
    if not session.get('logado'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Buscar todas as administrações da prescrição
    cursor.execute("""
        SELECT 
            a.id_administracao,
            a.dose_aplicada,
            a.data_aplicacao,
            pac.nome AS paciente,
            m.nome AS medicamento
        FROM administracao a
        JOIN prescricao p ON a.id_prescricao = p.id_prescricao
        JOIN paciente pac ON p.id_paciente = pac.id_paciente
        JOIN medicamento m ON p.id_medicamento = m.id_medicamento
        WHERE p.id_prescricao = %s
        ORDER BY a.data_aplicacao DESC
    """, (id_prescricao,))

    historico = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('historico_administracao.html', historico=historico)


if __name__ == '__main__':
    app.run(debug=True)
