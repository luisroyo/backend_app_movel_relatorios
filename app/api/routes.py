# app/api/routes.py
from flask import jsonify, request
from app.api import api_bp
from app.models import Ronda, User
from app import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime # Importar datetime para o timestamp

# --- Endpoint de Login ---
@api_bp.route('/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"msg": "Faltam o nome de utilizador ou a senha"}), 400

    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id)) # Identidade como string
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Nome de utilizador ou senha inválidos"}), 401

# --- Endpoints de Rondas (Protegidos) ---

@api_bp.route('/rondas', methods=['GET'])
@jwt_required()
def get_rondas():
    current_user_id = int(get_jwt_identity()) # Converter para int se user.id for int
    # Filtrar rondas pelo utilizador atual (boa prática)
    rondas = Ronda.query.filter_by(user_id=current_user_id).all()
    # Se quiser que um admin veja todas, adicione lógica de permissões aqui
    # rondas = Ronda.query.all() # Como estava antes, lista todas as rondas
    return jsonify([ronda.to_dict() for ronda in rondas]), 200

@api_bp.route('/rondas/<int:ronda_id>', methods=['GET'])
@jwt_required()
def get_ronda(ronda_id):
    current_user_id = int(get_jwt_identity())
    ronda = db.session.get(Ronda, ronda_id)
    
    if ronda is None:
        return jsonify({'error': 'Ronda não encontrada'}), 404
    
    # Verificar se a ronda pertence ao utilizador atual
    if ronda.user_id != current_user_id:
        # Adicionar lógica aqui se um admin puder ver rondas de outros
        return jsonify({'error': 'Acesso não autorizado a esta ronda'}), 403
    
    return jsonify(ronda.to_dict()), 200

@api_bp.route('/rondas', methods=['POST'])
@jwt_required()
def create_ronda():
    current_user_id = int(get_jwt_identity())
    # data = request.get_json() or {} # Para dados adicionais no futuro

    user = db.session.get(User, current_user_id)
    if not user:
        return jsonify({'error': 'Utilizador do token não encontrado'}), 404

    nova_ronda = Ronda(user_id=current_user_id)
    
    db.session.add(nova_ronda)
    db.session.commit()

    return jsonify(nova_ronda.to_dict()), 201

# --- NOVO ENDPOINT: Finalizar uma Ronda ---
@api_bp.route('/rondas/<int:ronda_id>/finalizar', methods=['PUT'])
@jwt_required()
def finalizar_ronda(ronda_id):
    current_user_id = int(get_jwt_identity()) # Obtém o ID do utilizador do token

    ronda = db.session.get(Ronda, ronda_id)

    if ronda is None:
        return jsonify({'msg': 'Ronda não encontrada'}), 404

    # Verificar se a ronda pertence ao utilizador autenticado
    if ronda.user_id != current_user_id:
        return jsonify({'msg': 'Não autorizado a finalizar esta ronda'}), 403

    # Verificar se a ronda já foi finalizada
    if ronda.fim_ronda is not None:
        return jsonify({'msg': 'Esta ronda já foi finalizada'}), 400 # Bad Request

    ronda.fim_ronda = datetime.utcnow() # Define a hora de fim para agora
    db.session.commit()

    return jsonify(ronda.to_dict()), 200
