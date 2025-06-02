from flask import Flask, render_template, request, redirect, flash
import os
import logging
import sys
import sqlite3

# Configuração de Caminhos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

app = Flask(__name__)
app.secret_key = 'super-secret-xp-key'
app.config['DATABASE_PATH'] = os.path.join(BASE_DIR, 'todo.db')

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, "log.txt")),
        logging.StreamHandler()
    ]
)

# =========================
# Funções de Banco de Dados
# =========================

def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE_PATH'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            category TEXT NOT NULL,
            priority INTEGER DEFAULT 2,
            done BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def db_exists():
    return os.path.exists(app.config['DATABASE_PATH'])

def add_task(task, category, priority=2):
    conn = get_db_connection()
    conn.execute('INSERT INTO tasks (task, category, priority) VALUES (?, ?, ?)',
                (task, category, priority))
    conn.commit()
    conn.close()

def get_tasks_by_category(category=None):
    conn = get_db_connection()
    
    if category:
        tasks = conn.execute(
            'SELECT id, task, category, priority, done FROM tasks WHERE category = ? AND done = 0 ORDER BY priority ASC, created_at DESC',
            (category,)
        ).fetchall()
    else:
        tasks = conn.execute(
            'SELECT id, task, category, priority, done FROM tasks WHERE done = 0 ORDER BY category, priority ASC, created_at DESC'
        ).fetchall()
    
    conn.close()
    return tasks

def get_all_categories():
    conn = get_db_connection()
    categories = conn.execute(
        'SELECT DISTINCT category FROM tasks ORDER BY category'
    ).fetchall()
    conn.close()
    return [cat['category'] for cat in categories]

def mark_task_done(task_id):
    conn = get_db_connection()
    conn.execute('UPDATE tasks SET done = 1 WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

# =========================
# Inicialização
# =========================

def startup_checks():
    logging.info("🧠 Inicializando aplicação To-Do List XP...")
    
    if db_exists():
        logging.info("✅ Banco de dados localizado com sucesso.")
    else:
        logging.warning("🚫 Banco de dados não encontrado! Criando novo banco...")
        try:
            init_db()
            logging.info("✅ Banco de dados criado com sucesso.")
            # Adiciona algumas tarefas de exemplo
            add_task("Reunião XP", "Trabalho", 1)
            add_task("Compras mercado", "Casa", 2)
            add_task("Estudar Python", "Estudos", 3)
            logging.info("✅ Tarefas de exemplo adicionadas.")
        except Exception as e:
            logging.critical(f"🔥 Erro ao criar o banco de dados: {e}")
            raise

# =========================
# Rotas
# =========================

@app.route('/')
def index():
    category_filter = request.args.get('category', '')
    
    try:
        # Busca todas as categorias para as abas
        categories = get_all_categories()
        
        # Busca as tarefas de acordo com o filtro
        if category_filter:
            tasks = get_tasks_by_category(category_filter)
            # Agrupamos em um dicionário com uma única chave (a categoria filtrada)
            tasks_by_category = {category_filter: tasks}
        else:
            # Busca todas as tarefas não concluídas
            tasks = get_tasks_by_category()
            # Agrupa por categoria
            tasks_by_category = {}
            for task in tasks:
                cat = task['category']
                if cat not in tasks_by_category:
                    tasks_by_category[cat] = []
                tasks_by_category[cat].append(task)
        
        return render_template(
            'index.html',
            tasks_by_category=tasks_by_category,
            categories=categories,
            current_category=category_filter
        )
    except Exception as e:
        logging.error(f"Erro ao buscar tarefas: {e}")
        flash("Erro ao carregar tarefas.", "error")
        return render_template('index.html', tasks_by_category={}, categories=[], current_category='')

@app.route('/add', methods=['POST'])
def add_task_route():
    task = request.form.get('task', '').strip()
    category = request.form.get('category', '').strip()
    priority = request.form.get('priority', '2').strip()

    if not task or not category:
        flash("Tarefa e categoria são obrigatórias.", "error")
        return redirect('/')
    
    try:
        priority_int = int(priority)
        if priority_int not in [1, 2, 3]:
            priority_int = 2
            
        add_task(task, category, priority_int)
        flash("Tarefa adicionada com sucesso!", "success")
    except ValueError:
        add_task(task, category)
        flash("Tarefa adicionada com prioridade padrão.", "warning")
    except Exception as e:
        logging.error(f"Erro ao adicionar tarefa: {e}")
        flash("Erro ao adicionar tarefa.", "error")
    return redirect('/')

@app.route('/done/<int:task_id>')
def mark_done(task_id):
    try:
        mark_task_done(task_id)
        flash("Tarefa marcada como concluída!", "success")
    except Exception as e:
        logging.error(f"Erro ao marcar tarefa: {e}")
        flash("Erro ao marcar tarefa.", "error")
    return redirect(request.referrer or '/')

# =========================
# Execução Local
# =========================

if __name__ == '__main__':
    try:
        startup_checks()
        logging.info("🚀 Servidor iniciado: http://127.0.0.1:5000")
        app.run(debug=True)
    except Exception as e:
        logging.critical(f"Erro fatal: {e}")