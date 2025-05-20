# app/api/__init__.py
from flask import Blueprint

# Cria um Blueprint chamado 'api', com um prefixo de URL para todas as rotas deste blueprint
# Todas as rotas definidas neste blueprint serão acessíveis via /api/v1/*
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Importa as rotas no final para evitar importações circulares
# Este arquivo (routes.py) será criado na próxima etapa
from . import routes