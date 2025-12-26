import tkinter as tk
from tkinter import ttk

class ReportsView:
    def __init__(self, parent, db_path: str):
        self.db_path = db_path
        
        self.frame = ttk.Frame(parent)
        ttk.Label(self.frame, text="Relatórios - Em desenvolvimento").pack(pady=20)