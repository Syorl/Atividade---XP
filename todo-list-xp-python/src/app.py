from flask import Flask, render_template, request, redirect, flash
import os
import logging
import sys

# =========================
# Configuração de Caminhos
# =========================
# Adiciona o diretório pai ao caminho de busca
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Agora importamos os módulos do database
from database.db import init_db, db_exists
from database.models import add_task, get_tasks_by_category, mark_task_done

# =========================
# Configuração do App
# =========================
app = Flask(__name__)
app.secret_key = 'super-secret-xp-key'
app.config['DATABASE_PATH'] = os.path.join(BASE_DIR, 'todo.db')

# Configura logs
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler("log.txt"),
        logging.StreamHandler()
    ]
)

# =========================
# Inicialização
# =========================

def startup_checks():
    logging.info("🧠 Inicializando aplicação To-Do List XP...")
    
    if db_exists(app.config['DATABASE_PATH']):
        logging.info("✅ Banco de dados localizado com sucesso.")
    else:
        logging.warning("🚫 Banco de dados não encontrado! Criando novo banco...")
        try:
            init_db()
            logging.info("✅ Banco de dados criado com sucesso.")
        except Exception as e:
            logging.critical(f"🔥 Erro ao criar o banco de dados: {e}")
            raise

# =========================
# Rotas
# =========================

@app.route('/')
def index():
    category = request.args.get('category', '')
    try:
        tasks = get_tasks_by_category(category) if category else []
        return render_template('index.html', tasks=tasks)
    except Exception as e:
        logging.error(f"Erro ao buscar tarefas: {e}")
        flash("Erro ao carregar tarefas.")
        return render_template('index.html', tasks=[])

@app.route('/add', methods=['POST'])
def add():
    task = request.form.get('task', '').strip()
    category = request.form.get('category', '').strip()

    if not task or not category:
        flash("Tarefa e categoria são obrigatórias.")
        return redirect('/')

    try:
        add_task(task, category)
        flash("Tarefa adicionada com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao adicionar tarefa: {e}")
        flash("Erro ao adicionar tarefa.")
    return redirect('/')

@app.route('/done/<int:task_id>')
def done(task_id):
    try:
        mark_task_done(task_id)
        flash("Tarefa marcada como concluída.")
    except Exception as e:
        logging.error(f"Erro ao marcar tarefa como concluída: {e}")
        flash("Erro ao marcar tarefa.")
    return redirect('/')

# =========================
# Execução Local
# =========================

if __name__ == '__main__':
    try:
        logging.info("🚀 Rodando em modo local - http://127.0.0.1:5000")
        init_db()  # Garantia adicional
        app.run(debug=True)
    except Exception as e:
        logging.critical(f"Erro fatal na inicialização: {e}")