import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import sqlite3
from datetime import date, timedelta

class Dashboard:
    def __init__(self, parent, db_path: str):
        self.db_path = db_path
        
        self.frame = ttk.Frame(parent)
        self._criar_interface()
        self._atualizar_dados()
    
    def _criar_interface(self):
        # Frame de cards (KPIs) - mais compacto
        cards_frame = ttk.Frame(self.frame)
        cards_frame.pack(fill=tk.X, padx=10, pady=10)

        self.cards = {}
        metricas = [
            ('total', 'Total Hoje', '#3498db'),
            ('confirmados', 'Confirmados', '#2ecc71'),
            ('aguardando', 'Aguardando', '#f39c12'),
            ('sem_resposta', 'Sem Resposta', '#e74c3c')
        ]

        for i, (key, label, cor) in enumerate(metricas):
            card = self._criar_card(cards_frame, label, "0", cor)
            card.grid(row=0, column=i, padx=5, sticky=(tk.W, tk.E))

        cards_frame.columnconfigure(0, weight=1)
        cards_frame.columnconfigure(1, weight=1)
        cards_frame.columnconfigure(2, weight=1)
        cards_frame.columnconfigure(3, weight=1)

        # Frame de gráficos - mais compacto
        graficos_frame = ttk.Frame(self.frame)
        graficos_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Gráfico de Pizza - menor
        self.fig_pizza = Figure(figsize=(4, 3), dpi=80)
        self.ax_pizza = self.fig_pizza.add_subplot(111)
        self.canvas_pizza = FigureCanvasTkAgg(self.fig_pizza, graficos_frame)
        self.canvas_pizza.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Gráfico de Barras - menor
        self.fig_barras = Figure(figsize=(4, 3), dpi=80)
        self.ax_barras = self.fig_barras.add_subplot(111)
        self.canvas_barras = FigureCanvasTkAgg(self.fig_barras, graficos_frame)
        self.canvas_barras.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Mensagem quando não há dados
        self.msg_frame = ttk.Frame(self.frame)
        self.msg_label = ttk.Label(
            self.msg_frame,
            text="📊 Adicione pacientes para ver as estatísticas do dashboard\n\nUse 'Pacientes > Novo Paciente' ou importe uma planilha",
            font=('Arial', 10),
            foreground='gray',
            justify=tk.CENTER,
            wraplength=500
        )
        self.msg_label.pack(pady=20)
        self.msg_frame.pack(fill=tk.BOTH, expand=True)

        # Botão Atualizar - mais compacto
        ttk.Button(
            self.frame,
            text="🔄 Atualizar",
            command=self._atualizar_dados
        ).pack(pady=5)

    def _criar_card(self, parent, titulo, valor, cor):
        card_frame = ttk.Frame(parent, relief=tk.RAISED, borderwidth=2)
        
        ttk.Label(
            card_frame,
            text=titulo,
            font=('Arial', 10)
        ).pack(pady=(10, 5))
        
        valor_label = ttk.Label(
            card_frame,
            text=valor,
            font=('Arial', 24, 'bold'),
            foreground=cor
        )
        valor_label.pack(pady=(0, 10))
        
        card_frame.valor_label = valor_label
        return card_frame
    
    def _atualizar_dados(self):
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()

            # Formatar data no formato DD/MM/YYYY (como armazenado no banco)
            hoje = date.today().strftime('%d/%m/%Y')

            # KPIs do dia
            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    COALESCE(SUM(CASE WHEN status = 'confirmado' THEN 1 ELSE 0 END), 0) as confirmados,
                    COALESCE(SUM(CASE WHEN status IN ('mensagem_preparada', 'mensagem_enviada') THEN 1 ELSE 0 END), 0) as aguardando,
                    COALESCE(SUM(CASE WHEN status = 'sem_resposta' THEN 1 ELSE 0 END), 0) as sem_resposta
                FROM pacientes
                WHERE data_consulta = ?
            """, (hoje,))

            result = cursor.fetchone()

            # Atualizar cards
            self.cards['total'].valor_label.config(text=str(result[0]))
            self.cards['confirmados'].valor_label.config(text=str(result[1]))
            self.cards['aguardando'].valor_label.config(text=str(result[2]))
            self.cards['sem_resposta'].valor_label.config(text=str(result[3]))

            # Mostrar/ocultar mensagem de ajuda
            if result[0] == 0:
                self.msg_label.config(text="📊 Adicione pacientes para ver as estatísticas do dashboard\n\nUse 'Pacientes > Novo Paciente' ou importe uma planilha")
            else:
                self.msg_label.config(text="")

            # Dados para gráfico de pizza
            labels = ['Confirmados', 'Aguardando', 'Sem Resposta', 'Outros']
            sizes = [result[1], result[2], result[3], result[0] - (result[1] + result[2] + result[3])]
            colors = ['#2ecc71', '#f39c12', '#e74c3c', '#95a5a6']

            # Atualizar gráfico de pizza
            self.ax_pizza.clear()
            if sum(sizes) > 0:
                self.ax_pizza.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            else:
                self.ax_pizza.text(0.5, 0.5, 'Sem dados\npara hoje', ha='center', va='center', transform=self.ax_pizza.transAxes, fontsize=12)
            self.ax_pizza.set_title('Distribuição de Status - Hoje')
            self.canvas_pizza.draw()

            # Dados últimos 7 dias
            datas = []
            confirmados_por_dia = []

            for i in range(6, -1, -1):
                data_obj = date.today() - timedelta(days=i)
                data_formatada = data_obj.strftime('%d/%m/%Y')  # Formato DD/MM/YYYY
                datas.append(data_obj.strftime('%m-%d'))  # MM-DD para exibição

                cursor.execute("""
                    SELECT COUNT(*)
                    FROM pacientes
                    WHERE data_consulta = ? AND status = 'confirmado'
                """, (data_formatada,))

                confirmados_por_dia.append(cursor.fetchone()[0])

            conn.close()

            # Atualizar gráfico de barras
            self.ax_barras.clear()
            self.ax_barras.bar(datas, confirmados_por_dia, color='#3498db')
            self.ax_barras.set_title('Confirmações - Últimos 7 Dias')
            self.ax_barras.set_xlabel('Data')
            self.ax_barras.set_ylabel('Confirmados')
            self.ax_barras.tick_params(axis='x', rotation=45)
            self.fig_barras.tight_layout()
            self.canvas_barras.draw()

        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                # Ignorar erro de lock e manter dados anteriores
                pass
            else:
                # Re-raise outros erros
                raise
        except Exception as e:
            # Para outros erros, também ignorar para não quebrar a interface
            pass