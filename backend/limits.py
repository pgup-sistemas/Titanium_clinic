import sqlite3
from datetime import datetime, date, timedelta
from typing import Dict, Tuple

class LimitsController:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def _get_connection(self):
        return sqlite3.connect(self.db_path, timeout=10)
    
    def verificar_limite_diario(self, tipo_mensagem: str = 'primeiro_contato') -> Tuple[bool, str]:
        """Verifica se limite diário foi atingido"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Obter limite configurado
        cursor.execute("""
            SELECT valor_limite FROM limites_sistema
            WHERE tipo_limite = 'max_primeiros_contatos_dia'
        """)
        
        limite_maximo = cursor.fetchone()[0]
        
        # Contar envios de hoje
        hoje = date.today().isoformat()
        cursor.execute("""
            SELECT COALESCE(SUM(total_enviado), 0)
            FROM controle_envio
            WHERE data = ? AND tipo_mensagem = ?
        """, (hoje, tipo_mensagem))
        
        total_hoje = cursor.fetchone()[0]
        conn.close()
        
        if total_hoje >= limite_maximo:
            return False, f'Limite diário atingido ({total_hoje}/{limite_maximo}). Aguarde até amanhã.'
        
        restantes = limite_maximo - total_hoje
        return True, f'{restantes} envios restantes hoje'
    
    def verificar_limite_por_numero(self, telefone: str) -> Tuple[bool, str]:
        """Verifica quantas vezes um número já foi contatado hoje"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        hoje = date.today().isoformat()
        
        cursor.execute("""
            SELECT total_enviado, ultimo_envio
            FROM controle_envio
            WHERE data = ? AND numero_telefone = ?
        """, (hoje, telefone))
        
        result = cursor.fetchone()
        
        # Obter limite de tentativas
        cursor.execute("""
            SELECT valor_limite FROM limites_sistema
            WHERE tipo_limite = 'max_tentativas_paciente'
        """)
        
        max_tentativas = cursor.fetchone()[0]
        conn.close()
        
        if result:
            total_enviado, ultimo_envio = result
            
            if total_enviado >= max_tentativas:
                return False, f'Número já contatado {total_enviado} vezes hoje. Limite: {max_tentativas}'
            
            # Verificar intervalo mínimo
            if ultimo_envio:
                ultimo = datetime.fromisoformat(ultimo_envio)
                intervalo = (datetime.now() - ultimo).total_seconds()
                
                if intervalo < 120:  # 2 minutos
                    return False, f'Aguarde {int(120 - intervalo)} segundos para contatar este número novamente'
        
        return True, 'Pode enviar'
    
    def registrar_envio(self, telefone: str, tipo_mensagem: str, usuario_id: int) -> Dict:
        """Registra envio no controle de limites"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        hoje = date.today().isoformat()
        agora = datetime.now().isoformat()
        
        try:
            # Verificar se já existe registro hoje para este número
            cursor.execute("""
                SELECT id, total_enviado FROM controle_envio
                WHERE data = ? AND numero_telefone = ?
            """, (hoje, telefone))
            
            result = cursor.fetchone()
            
            if result:
                # Atualizar contador
                registro_id, total = result
                cursor.execute("""
                    UPDATE controle_envio
                    SET total_enviado = ?,
                        ultimo_envio = ?,
                        usuario_id = ?
                    WHERE id = ?
                """, (total + 1, agora, usuario_id, registro_id))
            else:
                # Criar novo registro
                cursor.execute("""
                    INSERT INTO controle_envio 
                    (data, numero_telefone, tipo_mensagem, total_enviado, ultimo_envio, usuario_id)
                    VALUES (?, ?, ?, 1, ?, ?)
                """, (hoje, telefone, tipo_mensagem, agora, usuario_id))
            
            conn.commit()
            
            return {'success': True, 'message': 'Envio registrado'}
        
        except Exception as e:
            return {'success': False, 'message': f'Erro ao registrar: {str(e)}'}
        finally:
            conn.close()
    
    def obter_estatisticas_dia(self) -> Dict:
        """Retorna estatísticas de envios do dia"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        hoje = date.today().isoformat()
        
        cursor.execute("""
            SELECT 
                tipo_mensagem,
                SUM(total_enviado) as total,
                COUNT(DISTINCT numero_telefone) as numeros_unicos
            FROM controle_envio
            WHERE data = ?
            GROUP BY tipo_mensagem
        """, (hoje,))
        
        resultados = cursor.fetchall()
        conn.close()
        
        stats = {
            'data': hoje,
            'por_tipo': {}
        }
        
        for tipo, total, unicos in resultados:
            stats['por_tipo'][tipo] = {
                'total_envios': total,
                'numeros_unicos': unicos
            }
        
        return stats