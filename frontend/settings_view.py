import tkinter as tk
from tkinter import ttk

class SettingsView:
    def __init__(self, parent, db_path: str):
        self.db_path = db_path
        
        self.frame = ttk.Frame(parent)
        ttk.Label(self.frame, text="Configurações - Em desenvolvimento").pack(pady=20)