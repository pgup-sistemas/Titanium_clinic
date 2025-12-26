import tkinter as tk
from tkinter import ttk

class UserManagement:
    def __init__(self, parent, db_path: str):
        self.db_path = db_path
        
        self.frame = ttk.Frame(parent)
        ttk.Label(self.frame, text="Gestão de Usuários - Em desenvolvimento").pack(pady=20)