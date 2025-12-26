import logging
from datetime import datetime
import sqlite3

class AuditLogger:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._setup_logging()
    
    def _setup_logging(self):
        """Configura logging para arquivo"""
        logging.basicConfig(
            filename=f'data/logs/sistema_{datetime.now().strftime("%Y%m")}.log',
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def log_acao(self, usuario_id: int, acao: str, tabela: str = None, 
                 registro_id: int = None, detalhes: str = ''):
        """Registra ação no log de auditoria"""
        conn = sqlite3.connect(self.db_path, timeout=10)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO log_auditoria (usuario_id, acao, tabela, registro_id, dados_novos)
                VALUES (?, ?, ?, ?, ?)
            """, (usuario_id, acao, tabela, registro_id, detalhes))
            
            conn.commit()
            
            # Também log no arquivo
            logging.info(f"Usuario: {usuario_id} | Acao: {acao} | Tabela: {tabela} | ID: {registro_id} | Detalhes: {detalhes}")
        
        except Exception as e:
            logging.error(f"Erro ao registrar auditoria: {str(e)}")
        finally:
            conn.close()
    
    def log_erro(self, erro: str, contexto: str = ''):
        """Registra erro no log"""
        logging.error(f"Erro: {erro} | Contexto: {contexto}")

def configurar_logs():
    """Função global para configurar logs"""
    logging.basicConfig(
        filename=f'data/logs/sistema_{datetime.now().strftime("%Y%m")}.log',
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def log_acao(usuario, acao, detalhes=''):
    logging.info(f"Usuario: {usuario} | Acao: {acao} | Detalhes: {detalhes}")

def log_erro(erro, contexto=''):
    logging.error(f"Erro: {erro} | Contexto: {contexto}")