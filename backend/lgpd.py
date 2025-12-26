import sqlite3
from datetime import datetime
from typing import Dict, Optional

class LGPDManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def _get_connection(self):
        return sqlite3.connect(self.db_path, timeout=10)
    
    def registrar_consentimento(self, paciente_id: int, forma: str,
                               usuario_id: int, observacoes: str = '') -> Dict:
        """Registra consentimento LGPD do paciente"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Obter versão atual do termo
            cursor.execute("""
                SELECT versao FROM termos_lgpd
                WHERE ativo = 1
                ORDER BY data_vigencia DESC
                LIMIT 1
            """)
            
            versao_termo = cursor.fetchone()
            if not versao_termo:
                return {
                    'success': False,
                    'message': 'Nenhum termo LGPD ativo encontrado'
                }
            
            versao = versao_termo[0]
            
            # Atualizar paciente
            cursor.execute("""
                UPDATE pacientes
                SET consentimento_whatsapp = 1,
                    data_consentimento = ?,
                    consentimento_obtido_por = ?,
                    forma_consentimento = ?,
                    termos_versao = ?,
                    observacoes = ?
                WHERE id = ?
            """, (datetime.now(), usuario_id, forma, versao, observacoes, paciente_id))
            
            conn.commit()
            
            # Log de auditoria
            from backend.audit import AuditLogger
            audit = AuditLogger(self.db_path)
            audit.log_acao(
                usuario_id,
                'consentimento_lgpd',
                'pacientes',
                paciente_id,
                f'Consentimento obtido de forma {forma}'
            )
            
            return {
                'success': True,
                'message': 'Consentimento registrado com sucesso'
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Erro ao registrar consentimento: {str(e)}'
            }
        finally:
            conn.close()
    
    def verificar_consentimento(self, paciente_id: int) -> bool:
        """Verifica se paciente deu consentimento"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT consentimento_whatsapp
            FROM pacientes
            WHERE id = ?
        """, (paciente_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result and result[0] == 1
    
    def revogar_consentimento(self, paciente_id: int, usuario_id: int) -> Dict:
        """Permite que paciente revogue consentimento"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE pacientes
            SET consentimento_whatsapp = 0
            WHERE id = ?
        """, (paciente_id,))
        
        conn.commit()
        
        # Log de auditoria
        from backend.audit import AuditLogger
        audit = AuditLogger(self.db_path)
        audit.log_acao(
            usuario_id,
            'revogacao_consentimento',
            'pacientes',
            paciente_id,
            'Consentimento revogado pelo paciente'
        )
        
        conn.close()
        
        return {
            'success': True,
            'message': 'Consentimento revogado. Paciente não receberá mais mensagens.'
        }
    
    def obter_termo_atual(self) -> Optional[str]:
        """Obtém texto do termo LGPD atual"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT texto_completo FROM termos_lgpd
            WHERE ativo = 1
            ORDER BY data_vigencia DESC
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def gerar_relatorio_consentimentos(self, data_inicio: str, data_fim: str) -> Dict:
        """Gera relatório de consentimentos por período"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN consentimento_whatsapp = 1 THEN 1 ELSE 0 END) as com_consentimento,
                SUM(CASE WHEN consentimento_whatsapp = 0 THEN 1 ELSE 0 END) as sem_consentimento,
                forma_consentimento,
                COUNT(*) as qtd
            FROM pacientes
            WHERE data_consentimento BETWEEN ? AND ?
            GROUP BY forma_consentimento
        """, (data_inicio, data_fim))
        
        resultados = cursor.fetchall()
        conn.close()
        
        return {
            'total': resultados[0][0] if resultados else 0,
            'com_consentimento': resultados[0][1] if resultados else 0,
            'sem_consentimento': resultados[0][2] if resultados else 0,
            'por_forma': [(r[3], r[4]) for r in resultados if r[3]]
        }