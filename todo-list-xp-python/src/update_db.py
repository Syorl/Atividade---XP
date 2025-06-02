import sqlite3

def update_database():
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    
    try:
        # Adicionar coluna de prioridade se não existir
        c.execute("ALTER TABLE tasks ADD COLUMN priority INTEGER DEFAULT 2")
        print("✅ Banco de dados atualizado com sucesso!")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️ Coluna de prioridade já existe")
        else:
            print(f"⚠️ Erro ao atualizar banco: {e}")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    update_database()