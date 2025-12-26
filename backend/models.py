import sqlite3
from typing import List, Dict, Optional
from datetime import datetime

class BaseModel:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def _get_connection(self):
        return sqlite3.connect(self.db_path, timeout=10)

class User(BaseModel):
    def __init__(self, db_path: str):
        super().__init__(db_path)
    
    def get_by_id(self, user_id: int) -> Optional[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, nome_completo, email, perfil, ativo
            FROM usuarios WHERE id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'username': row[1],
                'nome_completo': row[2],
                'email': row[3],
                'perfil': row[4],
                'ativo': row[5]
            }
        return None

class Patient(BaseModel):
    def __init__(self, db_path: str):
        super().__init__(db_path)
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, nome, telefone, data_consulta, hora_consulta, status
            FROM pacientes
            ORDER BY data_consulta DESC, hora_consulta DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            'id': row[0],
            'nome': row[1],
            'telefone': row[2],
            'data_consulta': row[3],
            'hora_consulta': row[4],
            'status': row[5]
        } for row in rows]
    
    def get_by_id(self, patient_id: int) -> Optional[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM pacientes WHERE id = ?
        """, (patient_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(zip([
                'id', 'nome', 'telefone', 'telefone_formatado', 'email', 'data_nascimento', 'cpf',
                'data_consulta', 'hora_consulta', 'tipo_consulta', 'profissional', 'observacoes',
                'status', 'mensagem_preparada', 'fase_conversa', 'data_preparo', 'data_envio', 'data_resposta',
                'consentimento_whatsapp', 'data_consentimento', 'consentimento_obtido_por', 'forma_consentimento', 'termos_versao',
                'tentativas_contato', 'ultima_tentativa', 'numero_valido', 'whatsapp_ativo',
                'data_cadastro', 'cadastrado_por', 'data_atualizacao', 'atualizado_por'
            ], row))
        return None
    
    def update_status(self, patient_id: int, status: str, user_id: int) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE pacientes
                SET status = ?, data_atualizacao = ?, atualizado_por = ?
                WHERE id = ?
            """, (status, datetime.now(), user_id, patient_id))
            
            conn.commit()
            return True
        except:
            return False
        finally:
            conn.close()

class Message(BaseModel):
    def __init__(self, db_path: str):
        super().__init__(db_path)
    
    def get_by_type(self, msg_type: str) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, texto FROM mensagens
            WHERE tipo = ? AND ativo = 1
        """, (msg_type,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{'id': row[0], 'texto': row[1]} for row in rows]