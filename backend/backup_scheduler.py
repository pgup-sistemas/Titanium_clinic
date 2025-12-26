"""
Scheduler para execução automática de backups
Executa em thread separada e verifica horário configurado
"""

import threading
import time
import sqlite3
from datetime import datetime, time as dt_time
from pathlib import Path
import logging

from backend.backup import BackupManager

class BackupScheduler:
    def __init__(self, db_path: str, backup_dir: str = 'data/backups'):
        self.db_path = db_path
        self.backup_dir = backup_dir
        self.backup_manager = BackupManager(db_path, backup_dir)
        self.running = False
        self.thread = None
        self._setup_logging()
    
    def _setup_logging(self):
        """Configura logging"""
        log_dir = Path('data/logs')
        log_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            filename=f'{log_dir}/backup_{datetime.now().strftime("%Y%m")}.log',
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('BackupScheduler')
    
    def _obter_configuracao_backup(self):
        """Obtém configurações de backup do banco"""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()
            
            # Verificar se backup automático está ativado
            cursor.execute("SELECT valor FROM configuracoes WHERE chave = 'backup_automatico'")
            result = cursor.fetchone()
            backup_auto = result and result[0].lower() == 'true' if result else True
            
            # Obter horário do backup
            cursor.execute("SELECT valor FROM configuracoes WHERE chave = 'backup_hora'")
            result = cursor.fetchone()
            backup_hora_str = result[0] if result else '23:00'
            
            # Obter dias de retenção
            cursor.execute("SELECT valor FROM configuracoes WHERE chave = 'dias_retencao_backup'")
            result = cursor.fetchone()
            dias_retencao = int(result[0]) if result else 7
            
            conn.close()
            
            # Parsear horário
            try:
                hora, minuto = map(int, backup_hora_str.split(':'))
                backup_time = dt_time(hora, minuto)
            except:
                backup_time = dt_time(23, 0)  # Padrão: 23:00
            
            return backup_auto, backup_time, dias_retencao
        
        except Exception as e:
            self.logger.error(f"Erro ao obter configuração: {str(e)}")
            return True, dt_time(23, 0), 7  # Valores padrão
    
    def _deve_executar_backup(self, backup_time: dt_time) -> bool:
        """Verifica se é hora de executar backup"""
        agora = datetime.now().time()
        
        # Verificar se já passou do horário hoje
        if agora >= backup_time:
            return True
        
        return False
    
    def _verificar_ultimo_backup_hoje(self) -> bool:
        """Verifica se já foi feito backup hoje"""
        hoje = datetime.now().date()
        
        # Procurar backup de hoje
        backup_dir = Path(self.backup_dir)
        if not backup_dir.exists():
            return False
        
        for arquivo in backup_dir.glob('titanium_backup_*.db'):
            try:
                # Extrair data do nome do arquivo (formato: titanium_backup_YYYYMMDD_HHMMSS.db)
                nome_parts = arquivo.stem.split('_')
                if len(nome_parts) >= 3:
                    data_str = nome_parts[2]  # YYYYMMDD
                    data_backup = datetime.strptime(data_str, '%Y%m%d').date()
                    
                    if data_backup == hoje:
                        return True
            except:
                continue
        
        return False
    
    def _executar_backup(self, dias_retencao: int):
        """Executa backup"""
        try:
            self.logger.info("Iniciando backup automático...")
            
            result = self.backup_manager.criar_backup()
            
            if result['success']:
                tamanho_mb = result['tamanho'] / (1024 * 1024)
                self.logger.info(f"✅ Backup criado: {result['arquivo']} ({tamanho_mb:.2f} MB)")
                
                # Limpar backups antigos
                removidos = self.backup_manager.limpar_backups_antigos(dias_retencao)
                if removidos > 0:
                    self.logger.info(f"🗑️ {removidos} backups antigos removidos")
            else:
                self.logger.error(f"❌ Erro no backup: {result.get('message', 'Erro desconhecido')}")
        
        except Exception as e:
            self.logger.error(f"Erro ao executar backup: {str(e)}")
    
    def _scheduler_loop(self):
        """Loop principal do scheduler"""
        self.logger.info("BackupScheduler iniciado")
        ultimo_backup_date = None
        
        while self.running:
            try:
                # Obter configurações
                backup_auto, backup_time, dias_retencao = self._obter_configuracao_backup()
                
                if not backup_auto:
                    # Backup automático desativado, aguardar 1 hora
                    time.sleep(3600)
                    continue
                
                agora = datetime.now()
                
                # Verificar se é hora de fazer backup
                if self._deve_executar_backup(backup_time):
                    # Verificar se já fez backup hoje
                    if ultimo_backup_date != agora.date():
                        if not self._verificar_ultimo_backup_hoje():
                            self._executar_backup(dias_retencao)
                            ultimo_backup_date = agora.date()
                        else:
                            self.logger.debug("Backup já foi executado hoje")
                            ultimo_backup_date = agora.date()
                
                # Aguardar 1 hora antes de verificar novamente
                time.sleep(3600)
            
            except Exception as e:
                self.logger.error(f"Erro no loop do scheduler: {str(e)}")
                time.sleep(3600)  # Aguardar 1 hora antes de tentar novamente
    
    def iniciar(self):
        """Inicia o scheduler em thread separada"""
        if self.running:
            self.logger.warning("Scheduler já está em execução")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.thread.start()
        self.logger.info("BackupScheduler iniciado em thread separada")
    
    def parar(self):
        """Para o scheduler"""
        if not self.running:
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        self.logger.info("BackupScheduler parado")
    
    def executar_backup_agora(self):
        """Executa backup manualmente (útil para testes)"""
        _, _, dias_retencao = self._obter_configuracao_backup()
        self._executar_backup(dias_retencao)

