import re
import validators
import phonenumbers
from datetime import datetime, time
from typing import Dict, Tuple

class SecurityValidator:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def validar_telefone(self, numero: str) -> Tuple[bool, str, str]:
        """
        Valida número de telefone brasileiro
        Retorna: (válido, número_formatado, mensagem_erro)
        """
        # Remover caracteres não numéricos
        numero_limpo = re.sub(r'[^\d+]', '', numero)
        
        # Adicionar código do país se não tiver
        if not numero_limpo.startswith('+'):
            numero_limpo = '+55' + numero_limpo
        
        try:
            telefone = phonenumbers.parse(numero_limpo)
            
            if not phonenumbers.is_valid_number(telefone):
                return False, '', 'Número de telefone inválido'
            
            # Verificar se é brasileiro
            if telefone.country_code != 55:
                return False, '', 'Sistema aceita apenas números brasileiros'
            
            # Formatar número
            numero_formatado = phonenumbers.format_number(
                telefone, 
                phonenumbers.PhoneNumberFormat.E164
            )
            
            return True, numero_formatado, ''
        
        except phonenumbers.NumberParseException:
            return False, '', 'Formato de número inválido'
    
    def validar_email(self, email: str) -> Tuple[bool, str]:
        """Valida formato de email"""
        if not email:
            return True, ''  # Email é opcional
        
        if not validators.email(email):
            return False, 'Email inválido'
        
        return True, ''
    
    def validar_cpf(self, cpf: str) -> Tuple[bool, str]:
        """Valida CPF brasileiro"""
        if not cpf:
            return True, ''  # CPF é opcional
        
        # Remover caracteres não numéricos
        cpf = re.sub(r'[^\d]', '', cpf)
        
        if len(cpf) != 11:
            return False, 'CPF deve ter 11 dígitos'
        
        # Verificar se todos os dígitos são iguais
        if cpf == cpf[0] * 11:
            return False, 'CPF inválido'
        
        # Validar dígitos verificadores
        def calcular_digito(cpf_parcial, peso_inicial):
            soma = sum(int(cpf_parcial[i]) * (peso_inicial - i) 
                      for i in range(len(cpf_parcial)))
            resto = soma % 11
            return 0 if resto < 2 else 11 - resto
        
        digito1 = calcular_digito(cpf[:9], 10)
        digito2 = calcular_digito(cpf[:10], 11)
        
        if cpf[-2:] != f"{digito1}{digito2}":
            return False, 'CPF inválido'
        
        return True, ''
    
    def verificar_horario_permitido(self) -> Tuple[bool, str]:
        """Verifica se está no horário permitido para envios"""
        import sqlite3

        conn = sqlite3.connect(self.db_path, timeout=10)
        cursor = conn.cursor()

        # Verificar se trabalha 24h
        cursor.execute("SELECT valor FROM configuracoes WHERE chave = 'trabalha_24h'")
        config_24h = cursor.fetchone()

        if config_24h and config_24h[0].lower() == 'true':
            conn.close()
            return True, 'Clínica trabalha 24 horas'

        cursor.execute("""
            SELECT valor_limite FROM limites_sistema
            WHERE tipo_limite IN ('horario_inicio', 'horario_fim')
        """)

        limites = cursor.fetchall()
        conn.close()

        if len(limites) < 2:
            return True, 'Limites não configurados'

        hora_inicio = int(limites[0][0])
        hora_fim = int(limites[1][0])

        hora_atual = datetime.now().hour

        if hora_atual < hora_inicio or hora_atual >= hora_fim:
            return False, f'Envios permitidos apenas entre {hora_inicio}h e {hora_fim}h'

        return True, ''
    
    def validar_intervalo_envio(self, ultimo_envio: datetime) -> Tuple[bool, str]:
        """Verifica intervalo mínimo entre envios"""
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT valor_limite FROM limites_sistema
            WHERE tipo_limite = 'intervalo_minimo_segundos'
        """)
        
        intervalo_minimo = cursor.fetchone()[0]
        conn.close()
        
        if ultimo_envio:
            tempo_decorrido = (datetime.now() - ultimo_envio).total_seconds()
            
            if tempo_decorrido < intervalo_minimo:
                segundos_faltantes = int(intervalo_minimo - tempo_decorrido)
                return False, f'Aguarde {segundos_faltantes} segundos antes do próximo envio'
        
        return True, ''