import sqlite3
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import os

class BackupManager:
    def __init__(self, db_path: str, backup_dir: str = 'data/backups'):
        self.db_path = db_path
        self.backup_dir = backup_dir
        Path(backup_dir).mkdir(parents=True, exist_ok=True)
    
    def criar_backup(self) -> dict:
        """Cria backup do banco de dados"""
        try:
            # Nome do arquivo de backup
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"{self.backup_dir}/titanium_backup_{timestamp}.db"
            
            # Copiar arquivo
            shutil.copy2(self.db_path, backup_file)
            
            # Comprimir (opcional)
            # import gzip
            # with open(backup_file, 'rb') as f_in:
            #     with gzip.open(f"{backup_file}.gz", 'wb') as f_out:
            #         shutil.copyfileobj(f_in, f_out)
            # os.remove(backup_file)
            
            return {
                'success': True,
                'arquivo': backup_file,
                'tamanho': os.path.getsize(backup_file)
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }
    
    def limpar_backups_antigos(self, dias_retencao: int = 7):
        """Remove backups mais antigos que N dias"""
        limite = datetime.now() - timedelta(days=dias_retencao)
        
        removidos = 0
        for arquivo in Path(self.backup_dir).glob('titanium_backup_*.db'):
            # Extrair data do nome do arquivo
            data_str = arquivo.stem.split('_')[2]  # YYYYMMDD
            data_backup = datetime.strptime(data_str, '%Y%m%d')
            
            if data_backup < limite:
                arquivo.unlink()
                removidos += 1
        
        return removidos
    
    def restaurar_backup(self, backup_file: str) -> bool:
        """Restaura banco de um backup"""
        try:
            if not Path(backup_file).exists():
                return False
            
            # Fazer backup do atual antes de restaurar
            self.criar_backup()
            
            # Restaurar
            shutil.copy2(backup_file, self.db_path)
            
            return True
        except:
            return False
    
    def listar_backups(self):
        """Lista todos os backups disponíveis"""
        backups = []
        
        for arquivo in sorted(Path(self.backup_dir).glob('titanium_backup_*.db'), reverse=True):
            stat = arquivo.stat()
            backups.append({
                'arquivo': str(arquivo),
                'nome': arquivo.name,
                'tamanho': stat.st_size,
                'data': datetime.fromtimestamp(stat.st_mtime)
            })
        
        return backups

# Executar backup diário automaticamente
def backup_automatico():
    """Função para ser chamada diariamente"""
    backup_mgr = BackupManager('data/titanium_clinica.db')
    
    # Criar backup
    result = backup_mgr.criar_backup()
    
    if result['success']:
        print(f"✅ Backup criado: {result['arquivo']}")
        
        # Limpar backups antigos
        removidos = backup_mgr.limpar_backups_antigos(7)
        if removidos > 0:
            print(f"🗑️ {removidos} backups antigos removidos")
    else:
        print(f"❌ Erro no backup: {result['message']}")

if __name__ == "__main__":
    backup_automatico()