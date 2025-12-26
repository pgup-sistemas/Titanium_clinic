import tkinter as tk
from tkinter import ttk, messagebox
from frontend.patient_view import PatientView
from frontend.message_preview import MessagePreview
from frontend.dashboard import Dashboard
from backend.auth import AuthManager

class MainWindow:
    def __init__(self, user_session: dict, db_path: str):
        self.user_session = user_session
        self.db_path = db_path
        self.auth_manager = AuthManager(db_path)
        
        self.window = tk.Tk()
        self.window.title(f"Titanium Clínica - {user_session['nome']} ({user_session['perfil']})")
        self.window.geometry("1200x700")
        
        self._criar_menu()
        self._criar_interface()
    
    def _criar_menu(self):
        menubar = tk.Menu(self.window)
        self.window.config(menu=menubar)
        
        # Menu Arquivo
        menu_arquivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=menu_arquivo)
        menu_arquivo.add_command(label="Configurações", command=self._abrir_configuracoes)
        menu_arquivo.add_separator()
        menu_arquivo.add_command(label="Sair", command=self._fazer_logout)
        
        # Menu Pacientes
        menu_pacientes = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Pacientes", menu=menu_pacientes)
        menu_pacientes.add_command(label="Novo Paciente", command=self._novo_paciente)
        menu_pacientes.add_command(label="Importar Planilha", command=self._importar_planilha)
        
        # Menu Relatórios (apenas gestor/admin)
        if self.user_session['perfil'] in ['admin', 'gestor']:
            menu_relatorios = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Relatórios", menu=menu_relatorios)
            menu_relatorios.add_command(label="Dashboard", command=self._abrir_dashboard)
            menu_relatorios.add_command(label="Gerar Relatório", command=self._gerar_relatorio)

        # Menu Mensagens (apenas admin)
        if self.user_session['perfil'] == 'admin':
            menu_mensagens = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Mensagens", menu=menu_mensagens)
            menu_mensagens.add_command(label="Gerenciar Mensagens", command=self._gerenciar_mensagens)

        # Menu Usuários (apenas admin)
        if self.user_session['perfil'] == 'admin':
            menu_usuarios = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Usuários", menu=menu_usuarios)
            menu_usuarios.add_command(label="Gerenciar Usuários", command=self._gerenciar_usuarios)
        
        # Menu Ajuda
        menu_ajuda = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=menu_ajuda)
        menu_ajuda.add_command(label="Manual do Usuário", command=self._abrir_manual)
        menu_ajuda.add_command(label="Sobre", command=self._sobre)
    
    def _criar_interface(self):
        # Notebook (abas)
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Aba Pacientes
        self.patient_view = PatientView(
            self.notebook,
            self.db_path,
            self.user_session,
            on_preparar_mensagem=self._preparar_mensagem
        )
        self.notebook.add(self.patient_view.frame, text="📋 Pacientes")
        
        # Aba Dashboard (se tiver permissão)
        if self.user_session['perfil'] in ['admin', 'gestor']:
            self.dashboard = Dashboard(self.notebook, self.db_path)
            self.notebook.add(self.dashboard.frame, text="📊 Dashboard")
            # Atualizar dados quando aba for selecionada
            self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_change)
    
    def _preparar_mensagem(self, paciente_id: int):
        """Abre janela de preview da mensagem"""
        MessagePreview(
            self.window,
            self.db_path,
            paciente_id,
            self.user_session,
            on_enviado=self.patient_view.atualizar_lista
        )
    
    def _fazer_logout(self):
        if messagebox.askyesno("Sair", "Deseja realmente sair do sistema?"):
            self.auth_manager.logout(self.user_session['token'])
            self.window.destroy()
    
    def _novo_paciente(self):
        from frontend.dialogs import PatientDialog
        PatientDialog(
            self.window,
            self.db_path,
            self.user_session,
            on_save_callback=self.patient_view.atualizar_lista
        )
    
    def _importar_planilha(self):
        from frontend.dialogs import ImportDialog
        ImportDialog(
            self.window,
            self.db_path,
            self.user_session,
            on_import_callback=self.patient_view.atualizar_lista
        )
    
    def _on_tab_change(self, event):
        """Atualiza dados do dashboard quando a aba é selecionada"""
        current_tab = self.notebook.index(self.notebook.select())
        if current_tab == 1 and hasattr(self, 'dashboard'):  # Aba Dashboard
            self.dashboard._atualizar_dados()

    def _abrir_dashboard(self):
        # Verificar se a aba dashboard existe (apenas para admin/gestor)
        if self.user_session['perfil'] in ['admin', 'gestor']:
            try:
                self.notebook.select(1)
            except:
                messagebox.showinfo("Dashboard", "Dashboard disponivel apenas para administradores e gestores")
        else:
            messagebox.showinfo("Acesso Restrito", "Dashboard disponivel apenas para administradores e gestores")
    
    def _gerar_relatorio(self):
        from frontend.dialogs import ReportDialog
        ReportDialog(self.window, self.db_path, self.user_session)
    
    def _abrir_configuracoes(self):
        if self.user_session['perfil'] in ['admin', 'gestor']:
            from frontend.dialogs import SettingsDialog
            SettingsDialog(self.window, self.db_path, self.user_session)
        else:
            messagebox.showinfo("Acesso Restrito", "Configurações disponíveis apenas para administradores e gestores")

    def _gerenciar_mensagens(self):
        from frontend.dialogs import MessageManagementDialog
        MessageManagementDialog(self.window, self.db_path, self.user_session)

    def _gerenciar_usuarios(self):
        from frontend.dialogs import UserManagementDialog
        UserManagementDialog(self.window, self.db_path, self.user_session)
    
    def _abrir_manual(self):
        import os
        manual_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs", "manual_usuario.md")
        try:
            os.startfile(manual_path)
        except OSError:
            # Fallback para sistemas que não suportam startfile
            import webbrowser
            webbrowser.open(manual_path)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o manual: {str(e)}")
    
    def _sobre(self):
        messagebox.showinfo(
            "Sobre",
            "Titanium Clínica v2.0\n"
            "Sistema de Confirmação Humanizada\n\n"
            "© 2025 - Todos os direitos reservados"
        )
    
    def run(self):
        self.window.protocol("WM_DELETE_WINDOW", self._fazer_logout)
        self.window.mainloop()