import tkinter as tk
from tkinter import messagebox, simpledialog
from frontend.login_window import LoginWindow
from frontend.main_window import MainWindow
from backend.database import criar_banco
from pathlib import Path
import sys

class TitaniumClinica:
    def __init__(self):
        self.db_path = 'data/titanium_clinica.db'
        self.user_session = None
        self.backup_scheduler = None
        
        # Verificar se banco existe
        if not Path(self.db_path).exists():
            self._primeira_execucao()
        
        # Iniciar backup automático
        self._iniciar_backup_automatico()
        
        # Iniciar login
        self._mostrar_login()
    
    def _iniciar_backup_automatico(self):
        """Inicia scheduler de backup automático"""
        try:
            from backend.backup_scheduler import BackupScheduler
            self.backup_scheduler = BackupScheduler(self.db_path)
            self.backup_scheduler.iniciar()
            print("✅ Backup automático iniciado")
        except Exception as e:
            print(f"⚠️  Erro ao iniciar backup automático: {str(e)}")
            self.backup_scheduler = None
    
    def _primeira_execucao(self):
        """Executado na primeira vez"""
        print("Primeira execucao detectada...")
        print("Criando banco de dados...")
        
        from backend.database import criar_banco, criar_usuario_admin
        
        criar_banco(self.db_path)
        
        # Solicitar credenciais do primeiro admin
        root = tk.Tk()
        root.withdraw()
        
        usuario = simpledialog.askstring(
            "Primeiro Acesso",
            "Crie um nome de usuário administrador:"
        )
        
        senha = simpledialog.askstring(
            "Primeiro Acesso",
            "Crie uma senha:",
            show='●'
        )
        
        if usuario and senha:
            criar_usuario_admin(self.db_path, usuario, senha)
            messagebox.showinfo(
                "Sucesso",
                f"Sistema configurado!\n\nUsuário: {usuario}\n\n"
                "Agora você pode fazer login."
            )
        else:
            messagebox.showerror("Erro", "Configuração cancelada")
            sys.exit(1)
        
        root.destroy()
        
        # Popular mensagens
        print("Gerando banco de mensagens...")
        from backend.populate_messages import popular_mensagens
        popular_mensagens(self.db_path)

        print("Sistema pronto!")
    
    def _mostrar_login(self):
        """Exibe tela de login"""
        login = LoginWindow(
            self.db_path,
            on_success_callback=self._login_sucesso
        )
        login.run()
    
    def _login_sucesso(self, user_session: dict):
        """Callback após login bem-sucedido"""
        self.user_session = user_session
        
        # Abrir janela principal
        main = MainWindow(user_session, self.db_path)
        main.run()
        
        # Quando fechar a janela principal, mostrar login novamente
        self._mostrar_login()
    
    def __del__(self):
        """Destrutor - para backup scheduler ao fechar"""
        if self.backup_scheduler:
            self.backup_scheduler.parar()

def main():
    app = TitaniumClinica()


if __name__ == "__main__":
    main()