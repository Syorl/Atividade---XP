# tests/test_app.py
import pytest
from src.app import app
from database.models import add_task, get_tasks_by_category
import sqlite3
import os

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DATABASE_PATH'] = ':memory:'  # Usar banco em memória para testes
    with app.test_client() as client:
        with app.app_context():
            # Inicializar banco de testes
            conn = sqlite3.connect(':memory:')
            c = conn.cursor()
            c.execute('''
                CREATE TABLE tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task TEXT NOT NULL,
                    category TEXT NOT NULL,
                    priority INTEGER NOT NULL DEFAULT 2,
                    done BOOLEAN NOT NULL DEFAULT 0
                )
            ''')
            conn.commit()
            conn.close()
        yield client

def test_add_task_with_priority(client):
    # Teste de adição com prioridade
    response = client.post('/add', data={
        'task': 'Teste XP',
        'category': 'Testes',
        'priority': '1'
    }, follow_redirects=True)
    
    assert b'Tarefa adicionada com sucesso' in response.data
    
    # Verificar se a prioridade foi salva corretamente
    tasks = get_tasks_by_category('Testes')
    assert len(tasks) == 1
    assert tasks[0]['priority'] == 1

def test_add_task_default_priority(client):
    # Teste sem especificar prioridade (deve usar padrão)
    response = client.post('/add', data={
        'task': 'Teste Default',
        'category': 'Testes'
    }, follow_redirects=True)
    
    assert b'Tarefa adicionada com sucesso' in response.data
    
    tasks = get_tasks_by_category('Testes')
    assert tasks[0]['priority'] == 2

def test_priority_ordering(client):
    # Adicionar tarefas com diferentes prioridades
    add_task('Baixa Prioridade', 'Testes', 3)
    add_task('Alta Prioridade', 'Testes', 1)
    add_task('Média Prioridade', 'Testes', 2)
    
    tasks = get_tasks_by_category('Testes')
    
    # Verificar ordenação: Alta > Média > Baixa
    assert tasks[0]['task'] == 'Alta Prioridade'
    assert tasks[1]['task'] == 'Média Prioridade'
    assert tasks[2]['task'] == 'Baixa Prioridade'