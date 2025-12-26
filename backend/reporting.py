import sqlite3
from datetime import date, datetime
from typing import Dict, List

class ReportingManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def _get_connection(self):
        return sqlite3.connect(self.db_path, timeout=10)
    
    def gerar_relatorio_diario(self, data: str = None) -> Dict:
        """Gera relatório diário de confirmações"""
        if not data:
            data = date.today().strftime('%d/%m/%Y')
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT
                COUNT(*) as total_pacientes,
                SUM(CASE WHEN status = 'confirmado' THEN 1 ELSE 0 END) as confirmados,
                SUM(CASE WHEN status IN ('mensagem_preparada', 'mensagem_enviada') THEN 1 ELSE 0 END) as aguardando,
                SUM(CASE WHEN status = 'sem_resposta' THEN 1 ELSE 0 END) as sem_resposta,
                SUM(CASE WHEN status = 'reagendado' THEN 1 ELSE 0 END) as reagendados,
                SUM(CASE WHEN status = 'cancelado' THEN 1 ELSE 0 END) as cancelados
            FROM pacientes
            WHERE data_consulta = ?
        """, (data,))
        
        result = cursor.fetchone()
        
        total = result[0] or 0
        confirmados = result[1] or 0
        
        taxa_confirmacao = (confirmados / total * 100) if total > 0 else 0
        
        # Salvar no relatório diário
        cursor.execute("""
            INSERT OR REPLACE INTO relatorios_diarios
            (data, total_pacientes, confirmados, aguardando_resposta, reagendados, sem_resposta, cancelados, taxa_confirmacao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (data, total, confirmados, result[2] or 0, result[4] or 0, result[3] or 0, result[5] or 0, taxa_confirmacao))
        
        conn.commit()
        conn.close()
        
        return {
            'data': data,
            'total_pacientes': total,
            'confirmados': confirmados,
            'aguardando': result[2] or 0,
            'sem_resposta': result[3] or 0,
            'reagendados': result[4] or 0,
            'cancelados': result[5] or 0,
            'taxa_confirmacao': round(taxa_confirmacao, 2)
        }
    
    def obter_estatisticas_gerais(self) -> Dict:
        """Retorna estatísticas gerais do sistema"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Total de pacientes
        cursor.execute("SELECT COUNT(*) FROM pacientes")
        total_pacientes = cursor.fetchone()[0]
        
        # Status atuais
        cursor.execute("""
            SELECT status, COUNT(*) 
            FROM pacientes 
            GROUP BY status
        """)
        
        status_counts = dict(cursor.fetchall())
        
        # Consentimentos LGPD
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN consentimento_whatsapp = 1 THEN 1 ELSE 0 END) as com_consentimento,
                SUM(CASE WHEN consentimento_whatsapp = 0 THEN 1 ELSE 0 END) as sem_consentimento
            FROM pacientes
        """)
        
        consentimentos = cursor.fetchone()
        
        # Usuários ativos
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE ativo = 1")
        usuarios_ativos = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_pacientes': total_pacientes,
            'status': status_counts,
            'consentimentos': {
                'com_consentimento': consentimentos[0] or 0,
                'sem_consentimento': consentimentos[1] or 0
            },
            'usuarios_ativos': usuarios_ativos
        }
    
    def relatorio_envios_periodo(self, data_inicio: str, data_fim: str) -> List[Dict]:
        """Relatório de envios por período"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT data, tipo_mensagem, SUM(total_enviado), COUNT(DISTINCT numero_telefone)
            FROM controle_envio
            WHERE data BETWEEN ? AND ?
            GROUP BY data, tipo_mensagem
            ORDER BY data
        """, (data_inicio, data_fim))
        
        resultados = cursor.fetchall()
        conn.close()
        
        relatorio = []
        for data, tipo, total, unicos in resultados:
            relatorio.append({
                'data': data,
                'tipo_mensagem': tipo,
                'total_envios': total,
                'numeros_unicos': unicos
            })
        
        return relatorio