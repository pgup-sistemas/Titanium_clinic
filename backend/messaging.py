import sqlite3
import random
from datetime import datetime
from typing import Optional, Dict

class MessageManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.ultimas_mensagens = {}  # Cache para evitar repetição
    
    def _get_connection(self):
        return sqlite3.connect(self.db_path, timeout=10)
    
    def gerar_mensagem(self, tipo: str, paciente_data: Dict) -> str:
        """
        Gera mensagem personalizada e humanizada
        
        Args:
            tipo: 'primeiro_contato', 'confirmacao', 'lembrete', 'reagendamento'
            paciente_data: Dicionário com dados do paciente
        
        Returns:
            Texto da mensagem personalizada
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Buscar mensagens do tipo solicitado
        cursor.execute("""
            SELECT id, texto FROM mensagens
            WHERE tipo = ? AND ativo = 1
        """, (tipo,))
        
        mensagens_disponiveis = cursor.fetchall()
        conn.close()
        
        if not mensagens_disponiveis:
            return self._mensagem_fallback(tipo, paciente_data)
        
        # Filtrar mensagens já usadas recentemente
        paciente_id = paciente_data.get('id')
        mensagens_usadas = self.ultimas_mensagens.get(paciente_id, set())
        
        mensagens_filtradas = [
            (mid, texto) for mid, texto in mensagens_disponiveis
            if mid not in mensagens_usadas
        ]
        
        # Se todas já foram usadas, limpar histórico
        if not mensagens_filtradas:
            mensagens_filtradas = mensagens_disponiveis
            self.ultimas_mensagens[paciente_id] = set()
        
        # Selecionar aleatoriamente
        msg_id, texto = random.choice(mensagens_filtradas)
        
        # Registrar uso
        if paciente_id:
            if paciente_id not in self.ultimas_mensagens:
                self.ultimas_mensagens[paciente_id] = set()
            self.ultimas_mensagens[paciente_id].add(msg_id)
        
        # Personalizar mensagem
        mensagem_final = self._personalizar_mensagem(texto, paciente_data)
        
        return mensagem_final
    
    def _personalizar_mensagem(self, texto: str, dados: Dict) -> str:
        """Substitui variáveis na mensagem"""
        # Formatar data (tentar múltiplos formatos)
        if dados.get('data_consulta'):
            data_obj = None
            # SQLite geralmente armazena DATE como YYYY-MM-DD
            formatos = ['%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y']
            
            for fmt in formatos:
                try:
                    data_obj = datetime.strptime(str(dados['data_consulta']), fmt)
                    break
                except (ValueError, TypeError):
                    continue
            
            if data_obj:
                data_formatada = data_obj.strftime('%d/%m/%Y')
                dia_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo'][data_obj.weekday()]
                texto = texto.replace('{data}', data_formatada)
                texto = texto.replace('{dia_semana}', dia_semana)
            else:
                # Data inválida ou formato desconhecido, usar valor original
                texto = texto.replace('{data}', str(dados['data_consulta']))
                texto = texto.replace('{dia_semana}', 'o dia')
        else:
            texto = texto.replace('{data}', 'hoje')
            texto = texto.replace('{dia_semana}', 'hoje')
        
        # Formatar hora
        if dados.get('hora_consulta'):
            try:
                hora_str = str(dados['hora_consulta'])[:5]
                texto = texto.replace('{hora}', hora_str)
            except:
                texto = texto.replace('{hora}', 'o horário agendado')
        else:
            texto = texto.replace('{hora}', 'agora')
        
        # Nome (usar apenas primeiro nome para ser mais pessoal)
        if dados.get('nome'):
            primeiro_nome = dados['nome'].split()[0]
            texto = texto.replace('{nome}', primeiro_nome)
        
        # Tipo de consulta/exame
        if dados.get('tipo_consulta'):
            texto = texto.replace('{tipo}', dados['tipo_consulta'])
        
        # Profissional
        if dados.get('profissional'):
            texto = texto.replace('{profissional}', dados['profissional'])
        
        return texto.strip()
    
    def _mensagem_fallback(self, tipo: str, dados: Dict) -> str:
        """Mensagem de emergência caso banco esteja vazio"""
        templates = {
            'primeiro_contato': f"Olá! Aqui é da clínica. Sua consulta está agendada para {dados.get('data_consulta', 'data')} às {dados.get('hora_consulta', 'hora')}. Tudo certo?",
            'confirmacao': f"Oi! Confirmando sua consulta para {dados.get('data_consulta', 'data')} às {dados.get('hora_consulta', 'hora')}. Pode confirmar?",
            'lembrete': f"Lembrete: sua consulta é amanhã, {dados.get('data_consulta', 'data')} às {dados.get('hora_consulta', 'hora')}. Nos vemos lá!",
            'reagendamento': "Entendi que precisa reagendar. Qual data seria melhor para você?"
        }
        
        return templates.get(tipo, "Olá! Entrando em contato da clínica.")
    
    def preparar_mensagem_paciente(self, paciente_id: int, tipo_mensagem: str) -> Dict:
        """Prepara mensagem para um paciente específico"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Buscar dados do paciente
        cursor.execute("""
            SELECT id, nome, telefone, data_consulta, hora_consulta,
                   tipo_consulta, profissional, status
            FROM pacientes
            WHERE id = ?
        """, (paciente_id,))
        
        paciente = cursor.fetchone()
        
        if not paciente:
            conn.close()
            return {'success': False, 'message': 'Paciente não encontrado'}
        
        paciente_data = {
            'id': paciente[0],
            'nome': paciente[1],
            'telefone': paciente[2],
            'data_consulta': paciente[3],
            'hora_consulta': paciente[4],
            'tipo_consulta': paciente[5],
            'profissional': paciente[6],
            'status': paciente[7]
        }
        
        # Gerar mensagem
        mensagem = self.gerar_mensagem(tipo_mensagem, paciente_data)
        
        # Salvar mensagem preparada
        agora = datetime.now().isoformat()
        
        cursor.execute("""
            UPDATE pacientes
            SET mensagem_preparada = ?,
                fase_conversa = ?,
                data_preparo = ?,
                status = 'mensagem_preparada'
            WHERE id = ?
        """, (mensagem, tipo_mensagem, agora, paciente_id))
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'mensagem': mensagem,
            'paciente': paciente_data
        }