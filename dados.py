import sqlite3, bcrypt


conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               username TEXT UNIQUE, 
               password BLOB)
               ''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS messages(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               sender TEXT NOT NULL,
               message TEXT NOT NULL ,
               timestamp TEXT NOT NULL)
               ''')

conn.commit()
conn.close()

def cria_user(nome, passwd):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    hashed_pass = bcrypt.hashpw(passwd.encode(), bcrypt.gensalt())


    try:
        cursor.execute('''
        INSERT INTO users (username, password)
        VALUES (?, ?)''', (nome, hashed_pass))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"[!] Usuário '{nome}' já existe.")
    finally:
        conn.close()

def valida_usuario(nome, passwd):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT password FROM users WHERE username = ? ''', (nome,))

    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        hashed = resultado[0]
        return bcrypt.checkpw(passwd.encode(), hashed)

    return False

def salva_mensagem(sender, mensagem, timestamp):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT into messages(sender, message, timestamp)
        VALUES (?,?,?)''', (sender, mensagem, timestamp) )
    
    conn.commit()
    conn.close()


def carregar_mensagens():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT sender, message, timestamp FROM messages
        ORDER BY id ASC
    ''')

    mensagens = cursor.fetchall()
    conn.close()
    return mensagens

