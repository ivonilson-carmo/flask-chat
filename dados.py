from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime


db = SQLAlchemy()


# cria tabelas
class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    senha_hash = db.Column(db.LargeBinary, nullable=False)


    def set_senha(self, senha):
        """ cria senha com hash"""
        self.senha_hash = generate_password_hash(senha).encode()
    
    def verifica_senha(self, senha):
        """ verifica senha informada com hash salvo """
        return check_password_hash(self.senha_hash.decode(), senha)


class Menssage(db.Model):
    __tablename__ = "mensagens"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id') ,nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    horario = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    usuario = db.relationship('Usuario', backref='mensagens')



# funcoes auxiliares

def cria_user(username, senha):
    """ cria novo usuario """
    if Usuario.query.filter_by(username=username).first():
        return False # user ja existe
    
    novo = Usuario(username=username)
    novo.set_senha(senha)

    db.session.add(novo)
    db.session.commit()
    return True

def valida_usuario(username, senha):
    """ Valida se existe login """
    user = Usuario.query.filter_by(username=username).first()
    if user and user.verifica_senha(senha):
        return True
    
    return False
    

def salva_mensagem(username, conteudo, horario):
    user = Usuario.query.filter_by(username=username).first()
    if not user:
        return False
    
    msg = Menssage(user_id=user.id, conteudo=conteudo, horario=horario)
    db.session.add(msg)
    db.session.commit()

    return True


def carregar_mensagens():
    """ carrega as mensagens ordenada por data """
    mensagens = Menssage.query.order_by(Menssage.horario.asc()).all()
    lista = []

    for msg in mensagens:
        lista.append({
            'nome': msg.usuario.username,
            'mensagem': msg.conteudo,
            'horario': msg.horario.strftime('%d/%m/%Y %H:%M')
        })
    
    return lista

