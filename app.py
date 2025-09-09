import eventlet

eventlet.monkey_patch()

from flask import Flask, render_template, request, redirect, url_for, session
from dados import db, valida_usuario, cria_user, carregar_mensagens, salva_mensagem
from flask_socketio import SocketIO, emit
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'minha_chave_secreta'
socketio = SocketIO(app, async_mode='eventlet')


app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()


def horario_formatado():
    agora = datetime.now()
    return agora.strftime("%d/%m/%Y às %H:%M")

@app.route("/")
def home():
    if 'user' in session:
        return redirect(url_for('chat'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        passwd = request.form['password']
        if valida_usuario(user, passwd):
            session['user'] = user
            return redirect(url_for('chat'))
        else:
            return render_template('login.html', erro="Usuário ou senha incorretos.")
    
    return render_template('login.html', erro=None)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form['username']
        passwd = request.form['password']
        confirm = request.form['confirm']
        if passwd != confirm:
            return render_template('register.html', erro="Senhas não coincidem.")
        
        if cria_user(user, passwd):
            session['user'] = user
            return redirect(url_for('chat'))
        
        return render_template('register.html', erro="Erro ao criar usuario, tente outro username!")
        


    
    return render_template('register.html', erro=None)


@app.route('/chat')
def chat():
    if 'user' not in session:
        return redirect(url_for('login'))

    mensagens = carregar_mensagens()
    return render_template('index.html', usuario=session['user'], mensagens=mensagens)


@socketio.on('mensagem')
def handle_msg(data):
    nome = data['user']
    texto = data['mensagem']
    horario = horario_formatado()

    salva_mensagem(nome, texto, datetime.now() )

    emit('mensagem_recebida', {'nome': nome, 'mensagem': texto, 'horario': horario}, broadcast=True)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))



if __name__ == '__main__':
    socketio.run(app, debug=True)