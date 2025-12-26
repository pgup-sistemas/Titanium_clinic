import bcrypt
import secrets
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict
import socket

class AuthManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def _get_connection(self):
        return sqlite3.connect(self.db_path, timeout=10)
    
    def hash_password(self, password: str) -> str:
        """Gera hash seguro da senha"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verifica se senha corresponde ao hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def criar_usuario(self, username: str, password: str, nome_completo: str,
                      email: str, perfil: str, criado_por: int) -> Dict:
        """Cria novo usuário no sistema"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            senha_hash = self.hash_password(password)
            
            cursor.execute("""
                INSERT INTO usuarios (username, senha_hash, nome_completo, 
                                    email, perfil, criado_por)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, senha_hash, nome_completo, email, perfil, criado_por))
            
            conn.commit()
            user_id = cursor.lastrowid
            
            return {
                'success': True,
                'user_id': user_id,
                'message': 'Usuário criado com sucesso'
            }
        except sqlite3.IntegrityError:
            return {
                'success': False,
                'message': 'Usuário ou email já existe'
            }
        finally:
            conn.close()
    
    def login(self, username: str, password: str) -> Dict:
        """Autentica usuário e cria sessão"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Buscar usuário
            cursor.execute("""
                SELECT id, senha_hash, nome_completo, perfil, ativo
                FROM usuarios
                WHERE username = ?
            """, (username,))
            
            user = cursor.fetchone()
            
            if not user:
                return {'success': False, 'message': 'Usuário não encontrado'}
            
            user_id, senha_hash, nome, perfil, ativo = user
            
            if not ativo:
                return {'success': False, 'message': 'Usuário inativo'}
            
            # Verificar senha
            if not self.verify_password(password, senha_hash):
                return {'success': False, 'message': 'Senha incorreta'}
            
            # Criar token de sessão
            token = secrets.token_urlsafe(32)
            ip_maquina = socket.gethostbyname(socket.gethostname())
            
            cursor.execute("""
                INSERT INTO sessoes (usuario_id, token, ip_maquina)
                VALUES (?, ?, ?)
            """, (user_id, token, ip_maquina))
            
            # Atualizar último acesso
            cursor.execute("""
                UPDATE usuarios
                SET ultimo_acesso = ?
                WHERE id = ?
            """, (datetime.now(), user_id))
            
            conn.commit()
            
            return {
                'success': True,
                'user_id': user_id,
                'nome': nome,
                'perfil': perfil,
                'token': token
            }
        finally:
            conn.close()
    
    def logout(self, token: str):
        """Encerra sessão do usuário"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE sessoes
                SET data_logout = ?, ativo = 0
                WHERE token = ?
            """, (datetime.now(), token))

            conn.commit()
        finally:
            if conn:
                conn.close()
    
    def verificar_sessao(self, token: str) -> Optional[Dict]:
        """Verifica se sessão é válida"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT s.usuario_id, u.nome_completo, u.perfil, s.data_login
            FROM sessoes s
            JOIN usuarios u ON s.usuario_id = u.id
            WHERE s.token = ? AND s.ativo = 1 AND u.ativo = 1
        """, (token,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        user_id, nome, perfil, data_login = result
        
        # Verificar se sessão não expirou (24 horas)
        if datetime.fromisoformat(data_login) < datetime.now() - timedelta(hours=24):
            self.logout(token)
            return None
        
        return {
            'user_id': user_id,
            'nome': nome,
            'perfil': perfil
        }
    
    def verificar_permissao(self, perfil: str, acao: str) -> bool:
        """Verifica se perfil tem permissão para ação"""
        permissoes = {
            'admin': ['*'],  # Todas as permissões
            'gestor': [
                'visualizar_dashboard',
                'gerar_relatorios',
                'gerenciar_usuarios',
                'configurar_sistema',
                'preparar_mensagem',
                'enviar_mensagem',
                'visualizar_pacientes'
            ],
            'atendente': [
                'preparar_mensagem',
                'enviar_mensagem',
                'visualizar_pacientes',
                'cadastrar_paciente',
                'atualizar_status'
            ]
        }
        
        acoes_perfil = permissoes.get(perfil, [])
        return '*' in acoes_perfil or acao in acoes_perfil