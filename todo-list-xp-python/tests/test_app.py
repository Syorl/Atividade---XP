import pytest
from database.db import init_db
from database.models import add_task, get_tasks_by_category, mark_task_done

def setup_module(module):
    init_db()

def test_add_task():
    add_task("Ler documentação Flask", "Estudo")
    tasks = get_tasks_by_category("Estudo")
    assert any("Ler documentação Flask" in t for t in tasks)

def test_mark_task_done():
    add_task("Criar testes", "Dev")
    tasks = get_tasks_by_category("Dev")
    task_id = tasks[-1][0]
    mark_task_done(task_id)
    updated = get_tasks_by_category("Dev")
    assert updated[-1][2] == 1

