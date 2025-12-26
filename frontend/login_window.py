import tkinter as tk
from tkinter import ttk, messagebox
from backend.auth import AuthManager

class LoginWindow:
    def __init__(self, db_path: str, on_success_callback):
        self.db_path = db_path
        self.on_success = on_success_callback
        self.auth_manager = AuthManager(db_path)
        
        self.window = tk.Tk()
        self.window.title("Titanium Clínica - Login")
        self.window.geometry("400x300")
        self.window.resizable(False, False)
        
        self._criar_interface()
        self._centralizar_janela()
    
    def _criar_interface(self):
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="40")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Logo/Título
        ttk.Label(
            main_frame,
            text="🦷 Titanium Clínica",
            font=('Arial', 18, 'bold')
        ).grid(row=0, column=0, columnspan=2, pady=(0, 30))
        
        # Usuário
        ttk.Label(main_frame, text="Usuário:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(main_frame, width=30)
        self.username_entry.grid(row=1, column=1, pady=5)
        
        # Senha
        ttk.Label(main_frame, text="Senha:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(main_frame, width=30, show="●")
        self.password_entry.grid(row=2, column=1, pady=5)
        
        # Botão Login
        ttk.Button(
            main_frame,
            text="Entrar",
            command=self._fazer_login
        ).grid(row=3, column=0, columnspan=2, pady=20)
        
        # Bind Enter
        self.password_entry.bind('<Return>', lambda e: self._fazer_login())
        
        # Focar no campo usuário
        self.username_entry.focus()
    
    def _fazer_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showwarning("Atenção", "Preencha usuário e senha")
            return
        
        # Autenticar
        result = self.auth_manager.login(username, password)
        
        if result['success']:
            self.window.destroy()
            self.on_success(result)
        else:
            messagebox.showerror("Erro", result['message'])
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus()
    
    def _centralizar_janela(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def run(self):
        self.window.mainloop()