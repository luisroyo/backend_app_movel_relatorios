# app/models.py
from app import db, login_manager # Supondo que db e login_manager estejam em app
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# ... (UserMixin e seu modelo User) ...
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256)) # Aumentado para 256
    rondas = db.relationship('Ronda', backref='vigilante', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self, include_email=False): # Adicionando to_dict para User também
        data = {
            'id': self.id,
            'username': self.username,
        }
        if include_email:
            data['email'] = self.email
        return data
    
    def __repr__(self):
        return f'<User {self.username}>'


class Ronda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inicio_ronda = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    fim_ronda = db.Column(db.DateTime, index=True, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ocorrencias = db.relationship('Ocorrencia', backref='ronda_pai', lazy='dynamic')
    pontos_verificados = db.relationship('PontoRonda', backref='ronda_associada', lazy='dynamic')

    def __repr__(self):
        return f'<Ronda {self.id} - User {self.user_id}>'

    # ----- MÉTODO to_dict() PARA RONDA -----
    def to_dict(self):
        data = {
            'id': self.id,
            'inicio_ronda': self.inicio_ronda.isoformat() if self.inicio_ronda else None,
            'fim_ronda': self.fim_ronda.isoformat() if self.fim_ronda else None,
            'user_id': self.user_id,
            # Você pode adicionar mais campos aqui, inclusive de relacionamentos.
            # Por exemplo, para obter o nome do usuário:
            # 'vigilante_username': self.vigilante.username if self.vigilante else None,
            # Para ocorrencias (será uma lista, precisa do to_dict em Ocorrencia):
            # 'ocorrencias': [ocorrencia.to_dict() for ocorrencia in self.ocorrencias]
        }
        return data
    # --------------------------------------

class Ocorrencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    ronda_id = db.Column(db.Integer, db.ForeignKey('ronda.id'))
    # Adicione outros campos conforme necessário

    def __repr__(self):
        return f'<Ocorrencia {self.id} - Ronda {self.ronda_id}>'

    def to_dict(self): # Adicionando to_dict para Ocorrencia
        return {
            'id': self.id,
            'descricao': self.descricao,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'ronda_id': self.ronda_id
        }

class PontoRonda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50))  # Ex: 'Verificado', 'Alerta', 'Normal'
    observacoes = db.Column(db.Text, nullable=True)
    timestamp_verificacao = db.Column(db.DateTime, default=datetime.utcnow)
    ronda_id = db.Column(db.Integer, db.ForeignKey('ronda.id'))

    def __repr__(self):
        return f'<PontoRonda {self.nome} - Ronda {self.ronda_id}>'

    def to_dict(self): # Adicionando to_dict para PontoRonda
        return {
            'id': self.id,
            'nome': self.nome,
            'status': self.status,
            'observacoes': self.observacoes,
            'timestamp_verificacao': self.timestamp_verificacao.isoformat() if self.timestamp_verificacao else None,
            'ronda_id': self.ronda_id
        }

# Adicione também o método to_dict() aos seus outros modelos (`Ocorrencia`, `PontoRonda`, etc.)
# de forma similar, se você for retorná-los diretamente ou aninhados em outras respostas da API.
# Dentro de app/models.py
# ... (outros imports e modelos) ...

class LoginHistory(db.Model): # Supondo que 'db' é sua instância SQLAlchemy
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45)) # Para IPv4 ou IPv6
    user_agent = db.Column(db.String(255))
    # Adicione outros campos que seu LoginHistory possa ter

    # Se você quiser que este modelo seja retornado pela API, adicione to_dict()
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        }

    def __repr__(self):
        return f'<LoginHistory {self.id} - User {self.user_id}>'