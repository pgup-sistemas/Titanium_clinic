import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from backend.security import SecurityValidator
from backend.lgpd import LGPDManager
import sqlite3
from datetime import datetime
import pandas as pd
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

class Dialogs:
    @staticmethod
    def show_info(title, message):
        messagebox.showinfo(title, message)

    @staticmethod
    def show_warning(title, message):
        messagebox.showwarning(title, message)

    @staticmethod
    def show_error(title, message):
        messagebox.showerror(title, message)

    @staticmethod
    def ask_yes_no(title, message):
        return messagebox.askyesno(title, message)

class PatientDialog:
    def __init__(self, parent, db_path, user_session, on_save_callback=None):
        self.parent = parent
        self.db_path = db_path
        self.user_session = user_session
        self.on_save_callback = on_save_callback
        self.security = SecurityValidator(db_path)

        self.window = tk.Toplevel(parent)
        self.window.title("Cadastrar Novo Paciente")
        self.window.geometry("500x600")
        self.window.resizable(False, False)
        self.window.grab_set()

        self._create_interface()
        self._center_window()

    def _create_interface(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        ttk.Label(
            main_frame,
            text="Cadastrar Novo Paciente",
            font=('Arial', 14, 'bold')
        ).pack(pady=(0, 20))

        # Formulário
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill=tk.X, pady=(0, 20))

        # Campos do formulário
        self.fields = {}

        # Nome
        ttk.Label(form_frame, text="Nome:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.fields['nome'] = ttk.Entry(form_frame, width=40)
        self.fields['nome'].grid(row=0, column=1, pady=5, padx=(10, 0))

        # Telefone
        ttk.Label(form_frame, text="Telefone:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.fields['telefone'] = ttk.Entry(form_frame, width=40)
        self.fields['telefone'].grid(row=1, column=1, pady=5, padx=(10, 0))

        # Email
        ttk.Label(form_frame, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.fields['email'] = ttk.Entry(form_frame, width=40)
        self.fields['email'].grid(row=2, column=1, pady=5, padx=(10, 0))

        # Data de nascimento
        ttk.Label(form_frame, text="Data Nasc.:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.fields['data_nascimento'] = ttk.Entry(form_frame, width=40)
        self.fields['data_nascimento'].grid(row=3, column=1, pady=5, padx=(10, 0))
        ttk.Label(form_frame, text="(DD/MM/YYYY)", font=('Arial', 8)).grid(row=3, column=2, padx=(5, 0))

        # CPF
        ttk.Label(form_frame, text="CPF:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.fields['cpf'] = ttk.Entry(form_frame, width=40)
        self.fields['cpf'].grid(row=4, column=1, pady=5, padx=(10, 0))

        # Data da consulta
        ttk.Label(form_frame, text="Data Consulta:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.fields['data_consulta'] = ttk.Entry(form_frame, width=40)
        self.fields['data_consulta'].grid(row=5, column=1, pady=5, padx=(10, 0))
        ttk.Label(form_frame, text="(DD/MM/YYYY)", font=('Arial', 8)).grid(row=5, column=2, padx=(5, 0))

        # Hora da consulta
        ttk.Label(form_frame, text="Hora Consulta:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.fields['hora_consulta'] = ttk.Entry(form_frame, width=40)
        self.fields['hora_consulta'].grid(row=6, column=1, pady=5, padx=(10, 0))
        ttk.Label(form_frame, text="(HH:MM)", font=('Arial', 8)).grid(row=6, column=2, padx=(5, 0))

        # Tipo de consulta
        ttk.Label(form_frame, text="Tipo Consulta:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.fields['tipo_consulta'] = ttk.Entry(form_frame, width=40)
        self.fields['tipo_consulta'].grid(row=7, column=1, pady=5, padx=(10, 0))

        # Profissional
        ttk.Label(form_frame, text="Profissional:").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.fields['profissional'] = ttk.Entry(form_frame, width=40)
        self.fields['profissional'].grid(row=8, column=1, pady=5, padx=(10, 0))

        # Observações
        ttk.Label(form_frame, text="Observações:").grid(row=9, column=0, sticky=tk.W, pady=5)
        self.fields['observacoes'] = tk.Text(form_frame, width=30, height=3)
        self.fields['observacoes'].grid(row=9, column=1, pady=5, padx=(10, 0))

        # Consentimento LGPD
        self.consentimento_var = tk.BooleanVar()
        ttk.Checkbutton(
            form_frame,
            text="Paciente autoriza envio de mensagens via WhatsApp",
            variable=self.consentimento_var
        ).grid(row=10, column=0, columnspan=3, pady=10, sticky=tk.W)

        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))

        ttk.Button(
            btn_frame,
            text="Salvar",
            command=self._salvar
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Cancelar",
            command=self.window.destroy
        ).pack(side=tk.RIGHT, padx=5)

    def _salvar(self):
        # Coletar dados
        dados = {}
        for campo, widget in self.fields.items():
            if isinstance(widget, tk.Text):
                dados[campo] = widget.get(1.0, tk.END).strip()
            else:
                dados[campo] = widget.get().strip()

        # Validações
        if not dados['nome']:
            messagebox.showerror("Erro", "Nome é obrigatório")
            return

        if not dados['telefone']:
            messagebox.showerror("Erro", "Telefone é obrigatório")
            return

        if not dados['data_consulta']:
            messagebox.showerror("Erro", "Data da consulta é obrigatória")
            return

        if not dados['hora_consulta']:
            messagebox.showerror("Erro", "Hora da consulta é obrigatória")
            return

        # Validar telefone
        valido, telefone_formatado, erro = self.security.validar_telefone(dados['telefone'])
        if not valido:
            messagebox.showerror("Erro", f"Telefone inválido: {erro}")
            return

        # Validar email se fornecido
        if dados['email']:
            valido, erro = self.security.validar_email(dados['email'])
            if not valido:
                messagebox.showerror("Erro", f"Email inválido: {erro}")
                return

        # Validar CPF se fornecido
        if dados['cpf']:
            valido, erro = self.security.validar_cpf(dados['cpf'])
            if not valido:
                messagebox.showerror("Erro", f"CPF inválido: {erro}")
                return

        # Validar datas
        try:
            if dados['data_nascimento']:
                datetime.strptime(dados['data_nascimento'], '%d/%m/%Y')
            if dados['data_consulta']:
                datetime.strptime(dados['data_consulta'], '%d/%m/%Y')
        except ValueError:
            messagebox.showerror("Erro", "Formato de data inválido. Use DD/MM/YYYY")
            return

        # Salvar no banco
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO pacientes (
                    nome, telefone, telefone_formatado, email, data_nascimento, cpf,
                    data_consulta, hora_consulta, tipo_consulta, profissional, observacoes,
                    cadastrado_por, data_cadastro
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dados['nome'],
                dados['telefone'],
                telefone_formatado,
                dados['email'] or None,
                dados['data_nascimento'] or None,
                dados['cpf'] or None,
                dados['data_consulta'] or None,
                dados['hora_consulta'] or None,
                dados['tipo_consulta'] or None,
                dados['profissional'] or None,
                dados['observacoes'] or None,
                self.user_session['user_id'],
                datetime.now()
            ))

            paciente_id = cursor.lastrowid

            # Registrar consentimento se fornecido
            if self.consentimento_var.get():
                lgpd = LGPDManager(self.db_path)
                lgpd.registrar_consentimento(
                    paciente_id,
                    'verbal',
                    self.user_session['user_id'],
                    'Consentimento obtido no cadastro'
                )

            conn.commit()
            conn.close()

            messagebox.showinfo("Sucesso", "Paciente cadastrado com sucesso!")
            self.window.destroy()

            if self.on_save_callback:
                self.on_save_callback()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")

    def _center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

class ReportDialog:
    def __init__(self, parent, db_path, user_session):
        self.parent = parent
        self.db_path = db_path
        self.user_session = user_session

        self.window = tk.Toplevel(parent)
        self.window.title("Gerar Relatórios")
        self.window.geometry("500x500")
        self.window.resizable(True, True)
        self.window.grab_set()

        self._create_interface()
        self._center_window()

    def _create_interface(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        ttk.Label(
            main_frame,
            text="Gerar Relatórios",
            font=('Arial', 14, 'bold')
        ).pack(pady=(0, 20))

        # Tipo de relatório
        type_frame = ttk.LabelFrame(main_frame, text="Tipo de Relatório", padding="10")
        type_frame.pack(fill=tk.X, pady=(0, 20))

        self.report_type = tk.StringVar(value="diario")

        ttk.Radiobutton(
            type_frame,
            text="Relatório Diário de Confirmações",
            variable=self.report_type,
            value="diario"
        ).pack(anchor=tk.W, pady=2)

        ttk.Radiobutton(
            type_frame,
            text="Relatório de Consentimentos LGPD",
            variable=self.report_type,
            value="lgpd"
        ).pack(anchor=tk.W, pady=2)

        ttk.Radiobutton(
            type_frame,
            text="Relatório de Envios por Período",
            variable=self.report_type,
            value="envios"
        ).pack(anchor=tk.W, pady=2)

        # Período (para relatórios de período)
        period_frame = ttk.LabelFrame(main_frame, text="Período", padding="10")
        period_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Label(period_frame, text="Data Inicial:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.data_inicial = ttk.Entry(period_frame, width=15)
        self.data_inicial.grid(row=0, column=1, pady=5, padx=(10, 0))

        ttk.Label(period_frame, text="Data Final:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.data_final = ttk.Entry(period_frame, width=15)
        self.data_final.grid(row=1, column=1, pady=5, padx=(10, 0))

        ttk.Label(period_frame, text="(DD/MM/YYYY)", font=('Arial', 8)).grid(row=0, column=2, padx=(5, 0))

        # Formato
        format_frame = ttk.LabelFrame(main_frame, text="Formato", padding="10")
        format_frame.pack(fill=tk.X, pady=(0, 20))

        self.format_type = tk.StringVar(value="tela")

        ttk.Radiobutton(
            format_frame,
            text="Exibir na Tela",
            variable=self.format_type,
            value="tela"
        ).pack(anchor=tk.W, pady=2)

        ttk.Radiobutton(
            format_frame,
            text="Salvar como PDF",
            variable=self.format_type,
            value="pdf"
        ).pack(anchor=tk.W, pady=2)

        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))

        ttk.Button(
            btn_frame,
            text="Gerar Relatório",
            command=self._gerar_relatorio
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Fechar",
            command=self.window.destroy
        ).pack(side=tk.RIGHT, padx=5)

    def _gerar_relatorio(self):
        tipo = self.report_type.get()
        formato = self.format_type.get()

        try:
            if tipo == "diario":
                self._relatorio_diario(formato)
            elif tipo == "lgpd":
                self._relatorio_lgpd(formato)
            elif tipo == "envios":
                self._relatorio_envios(formato)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {str(e)}")

    def _converter_data_para_sql(self, data_str: str) -> str:
        """Converte data de DD/MM/YYYY para YYYY-MM-DD"""
        try:
            if not data_str or not data_str.strip():
                return None
            partes = data_str.strip().split('/')
            if len(partes) == 3:
                return f"{partes[2]}-{partes[1]}-{partes[0]}"
            return data_str  # Já está no formato correto
        except:
            return data_str
    
    def _converter_data_para_exibicao(self, data_str: str) -> str:
        """Converte data de YYYY-MM-DD para DD/MM/YYYY"""
        try:
            if not data_str:
                return ''
            if '/' in data_str:
                return data_str  # Já está no formato correto
            partes = data_str.split('-')
            if len(partes) == 3:
                return f"{partes[2]}/{partes[1]}/{partes[0]}"
            return data_str
        except:
            return data_str

    def _relatorio_diario(self, formato):
        from backend.reporting import ReportingManager
        from datetime import date

        reporting = ReportingManager(self.db_path)
        # Usar formato DD/MM/YYYY que a função espera
        data = date.today().strftime('%d/%m/%Y')

        relatorio = reporting.gerar_relatorio_diario(data)

        if formato == "tela":
            msg = f"RELATÓRIO DIÁRIO - {relatorio['data']}\n\n"
            msg += f"Total de Pacientes: {relatorio['total_pacientes']}\n"
            msg += f"Confirmados: {relatorio['confirmados']}\n"
            msg += f"Aguardando Resposta: {relatorio['aguardando']}\n"
            msg += f"Sem Resposta: {relatorio['sem_resposta']}\n"
            msg += f"Reagendados: {relatorio['reagendados']}\n"
            msg += f"Cancelados: {relatorio['cancelados']}\n"
            msg += f"Taxa de Confirmação: {relatorio['taxa_confirmacao']}%\n"

            # Criar janela de resultado
            result_window = tk.Toplevel(self.window)
            result_window.title("Relatório Diário")
            result_window.geometry("400x300")

            text_widget = tk.Text(result_window, wrap=tk.WORD, padx=10, pady=10)
            text_widget.pack(fill=tk.BOTH, expand=True)
            text_widget.insert(1.0, msg)
            text_widget.config(state=tk.DISABLED)

        else:
            # Exportar PDF
            self._exportar_relatorio_diario_pdf(relatorio)

    def _relatorio_lgpd(self, formato):
        from backend.lgpd import LGPDManager

        # Obter datas dos campos de entrada
        data_inicio_str = self.data_inicial.get().strip()
        data_fim_str = self.data_final.get().strip()

        # Converter para formato SQL (YYYY-MM-DD)
        data_inicio = self._converter_data_para_sql(data_inicio_str) if data_inicio_str else "2024-01-01"
        data_fim = self._converter_data_para_sql(data_fim_str) if data_fim_str else "2024-12-31"

        lgpd = LGPDManager(self.db_path)
        relatorio = lgpd.gerar_relatorio_consentimentos(data_inicio, data_fim)

        if formato == "tela":
            msg = f"RELATÓRIO DE CONSENTIMENTOS LGPD\n\n"
            msg += f"Período: {self._converter_data_para_exibicao(data_inicio)} a {self._converter_data_para_exibicao(data_fim)}\n\n"
            msg += f"Total de Pacientes: {relatorio['total']}\n"
            msg += f"Com Consentimento: {relatorio['com_consentimento']}\n"
            msg += f"Sem Consentimento: {relatorio['sem_consentimento']}\n\n"
            msg += "Consentimentos por Forma:\n"

            for forma, qtd in relatorio['por_forma']:
                msg += f"- {forma}: {qtd}\n"

            # Criar janela de resultado
            result_window = tk.Toplevel(self.window)
            result_window.title("Relatório LGPD")
            result_window.geometry("400x300")

            text_widget = tk.Text(result_window, wrap=tk.WORD, padx=10, pady=10)
            text_widget.pack(fill=tk.BOTH, expand=True)
            text_widget.insert(1.0, msg)
            text_widget.config(state=tk.DISABLED)

        else:
            # Exportar PDF
            self._exportar_relatorio_lgpd_pdf(relatorio, data_inicio, data_fim)

    def _relatorio_envios(self, formato):
        from backend.reporting import ReportingManager

        # Obter datas dos campos de entrada
        data_inicio_str = self.data_inicial.get().strip()
        data_fim_str = self.data_final.get().strip()

        # Converter para formato SQL (YYYY-MM-DD)
        data_inicio = self._converter_data_para_sql(data_inicio_str) if data_inicio_str else "2024-01-01"
        data_fim = self._converter_data_para_sql(data_fim_str) if data_fim_str else "2024-12-31"

        reporting = ReportingManager(self.db_path)
        relatorio = reporting.relatorio_envios_periodo(data_inicio, data_fim)

        if formato == "tela":
            msg = f"RELATÓRIO DE ENVIOS POR PERÍODO\n\n"
            msg += f"Período: {self._converter_data_para_exibicao(data_inicio)} a {self._converter_data_para_exibicao(data_fim)}\n\n"

            for item in relatorio[:20]:  # Limitar a 20 primeiros
                msg += f"Data: {item['data']} | Tipo: {item['tipo_mensagem']} | Envios: {item['total_envios']} | Únicos: {item['numeros_unicos']}\n"

            if len(relatorio) > 20:
                msg += f"\n... e mais {len(relatorio) - 20} registros"

            # Criar janela de resultado
            result_window = tk.Toplevel(self.window)
            result_window.title("Relatório de Envios")
            result_window.geometry("500x400")

            text_widget = tk.Text(result_window, wrap=tk.WORD, padx=10, pady=10)
            text_widget.pack(fill=tk.BOTH, expand=True)
            text_widget.insert(1.0, msg)
            text_widget.config(state=tk.DISABLED)

        else:
            # Exportar PDF
            self._exportar_relatorio_envios_pdf(relatorio, data_inicio, data_fim)

    def _exportar_relatorio_diario_pdf(self, relatorio):
        """Exporta relatório diário para PDF"""
        try:
            # Selecionar local para salvar
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Salvar Relatório Diário",
                initialfile=f"relatorio_diario_{relatorio['data'].replace('/', '-')}.pdf"
            )

            if not filename:
                return

            # Criar PDF
            doc = SimpleDocTemplate(filename, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1  # Center
            )
            story.append(Paragraph(f"Relatório Diário - {relatorio['data']}", title_style))
            story.append(Spacer(1, 12))

            # Dados
            data = [
                ["Métrica", "Valor"],
                ["Total de Pacientes", str(relatorio['total_pacientes'])],
                ["Confirmados", str(relatorio['confirmados'])],
                ["Aguardando Resposta", str(relatorio['aguardando'])],
                ["Sem Resposta", str(relatorio['sem_resposta'])],
                ["Reagendados", str(relatorio['reagendados'])],
                ["Cancelados", str(relatorio['cancelados'])],
                ["Taxa de Confirmação", f"{relatorio['taxa_confirmacao']}%"]
            ]

            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            story.append(table)
            story.append(Spacer(1, 20))

            # Rodapé
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.grey
            )
            story.append(Paragraph(f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}", footer_style))

            doc.build(story)
            messagebox.showinfo("Sucesso", f"Relatório salvo em:\n{filename}")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar PDF: {str(e)}")

    def _exportar_relatorio_lgpd_pdf(self, relatorio, data_inicio: str, data_fim: str):
        """Exporta relatório LGPD para PDF"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Salvar Relatório LGPD",
                initialfile="relatorio_lgpd.pdf"
            )

            if not filename:
                return

            doc = SimpleDocTemplate(filename, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1
            )
            story.append(Paragraph("Relatório de Consentimentos LGPD", title_style))
            story.append(Spacer(1, 12))

            # Período
            periodo_texto = f"Período: {self._converter_data_para_exibicao(data_inicio)} a {self._converter_data_para_exibicao(data_fim)}"
            story.append(Paragraph(periodo_texto, styles['Normal']))
            story.append(Spacer(1, 12))

            # Dados gerais
            data_geral = [
                ["Métrica", "Valor"],
                ["Total de Pacientes", str(relatorio['total'])],
                ["Com Consentimento", str(relatorio['com_consentimento'])],
                ["Sem Consentimento", str(relatorio['sem_consentimento'])]
            ]

            table_geral = Table(data_geral)
            table_geral.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            story.append(table_geral)
            story.append(Spacer(1, 20))

            # Consentimentos por forma
            if relatorio['por_forma']:
                story.append(Paragraph("Consentimentos por Forma:", styles['Heading2']))
                story.append(Spacer(1, 12))

                data_forma = [["Forma", "Quantidade"]]
                for forma, qtd in relatorio['por_forma']:
                    data_forma.append([forma or 'Não informado', str(qtd)])

                table_forma = Table(data_forma)
                table_forma.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))

                story.append(table_forma)
                story.append(Spacer(1, 20))

            # Rodapé
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.grey
            )
            story.append(Paragraph(f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}", footer_style))

            doc.build(story)
            messagebox.showinfo("Sucesso", f"Relatório salvo em:\n{filename}")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar PDF: {str(e)}")

    def _exportar_relatorio_envios_pdf(self, relatorio, data_inicio: str, data_fim: str):
        """Exporta relatório de envios para PDF"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Salvar Relatório de Envios",
                initialfile="relatorio_envios.pdf"
            )

            if not filename:
                return

            doc = SimpleDocTemplate(filename, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1
            )
            story.append(Paragraph("Relatório de Envios por Período", title_style))
            story.append(Spacer(1, 12))

            # Período
            periodo_texto = f"Período: {self._converter_data_para_exibicao(data_inicio)} a {self._converter_data_para_exibicao(data_fim)}"
            story.append(Paragraph(periodo_texto, styles['Normal']))
            story.append(Spacer(1, 12))

            # Limitar a 50 registros para o PDF
            dados_limitados = relatorio[:50]

            # Tabela
            data = [["Data", "Tipo Mensagem", "Total Envios", "Números Únicos"]]
            for item in dados_limitados:
                data.append([
                    self._converter_data_para_exibicao(item['data']),
                    item['tipo_mensagem'],
                    str(item['total_envios']),
                    str(item['numeros_unicos'])
                ])

            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8)
            ]))

            story.append(table)

            if len(relatorio) > 50:
                story.append(Spacer(1, 12))
                story.append(Paragraph(f"... e mais {len(relatorio) - 50} registros", styles['Normal']))

            story.append(Spacer(1, 20))

            # Rodapé
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.grey
            )
            story.append(Paragraph(f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}", footer_style))

            doc.build(story)
            messagebox.showinfo("Sucesso", f"Relatório salvo em:\n{filename}")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar PDF: {str(e)}")

    def _center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

class UserManagementDialog:
    def __init__(self, parent, db_path, user_session):
        self.parent = parent
        self.db_path = db_path
        self.user_session = user_session

        self.window = tk.Toplevel(parent)
        self.window.title("Gerenciamento de Usuários")
        self.window.geometry("700x500")
        self.window.resizable(True, True)
        self.window.grab_set()

        self._create_interface()
        self._load_users()
        self._center_window()

    def _create_interface(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        ttk.Label(
            main_frame,
            text="Gerenciamento de Usuários",
            font=('Arial', 14, 'bold')
        ).pack(pady=(0, 20))

        # Lista de usuários
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Treeview
        columns = ('username', 'nome', 'perfil', 'ativo', 'ultimo_acesso')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)

        self.tree.heading('username', text='Usuário')
        self.tree.heading('nome', text='Nome Completo')
        self.tree.heading('perfil', text='Perfil')
        self.tree.heading('ativo', text='Ativo')
        self.tree.heading('ultimo_acesso', text='Último Acesso')

        self.tree.column('username', width=100)
        self.tree.column('nome', width=200)
        self.tree.column('perfil', width=80)
        self.tree.column('ativo', width=60)
        self.tree.column('ultimo_acesso', width=120)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Button(
            btn_frame,
            text="Novo Usuário",
            command=self._novo_usuario
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Editar",
            command=self._editar_usuario
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Ativar/Desativar",
            command=self._toggle_ativo
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Alterar Senha",
            command=self._alterar_senha
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Excluir",
            command=self._excluir_usuario
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Fechar",
            command=self.window.destroy
        ).pack(side=tk.RIGHT, padx=5)

    def _load_users(self):
        """Carrega lista de usuários"""
        # Limpar lista
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT username, nome_completo, perfil, ativo, ultimo_acesso
            FROM usuarios
            ORDER BY username
        """)

        for row in cursor.fetchall():
            username, nome, perfil, ativo, ultimo_acesso = row
            ativo_str = "Sim" if ativo else "Não"
            ultimo_acesso_str = ultimo_acesso[:10] if ultimo_acesso else "Nunca"

            self.tree.insert('', tk.END, values=(username, nome, perfil, ativo_str, ultimo_acesso_str))

        conn.close()

    def _novo_usuario(self):
        """Cria novo usuário"""
        dialog = UserDialog(self.window, self.db_path, self.user_session, on_save_callback=self._load_users)
        dialog.window.wait_window()

    def _editar_usuario(self):
        """Edita usuário selecionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Atenção", "Selecione um usuário")
            return

        username = self.tree.item(selection[0])['values'][0]
        dialog = UserDialog(self.window, self.db_path, self.user_session, username=username, on_save_callback=self._load_users)
        dialog.window.wait_window()

    def _toggle_ativo(self):
        """Ativa/desativa usuário"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Atenção", "Selecione um usuário")
            return

        username = self.tree.item(selection[0])['values'][0]

        if messagebox.askyesno("Confirmar", f"Alterar status do usuário {username}?"):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT ativo FROM usuarios WHERE username = ?", (username,))
            ativo_atual = cursor.fetchone()[0]

            cursor.execute(
                "UPDATE usuarios SET ativo = ? WHERE username = ?",
                (0 if ativo_atual else 1, username)
            )

            conn.commit()
            conn.close()

            self._load_users()
            messagebox.showinfo("Sucesso", "Status alterado com sucesso")

    def _alterar_senha(self):
        """Altera senha do usuário"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Atenção", "Selecione um usuário")
            return

        username = self.tree.item(selection[0])['values'][0]
        dialog = PasswordDialog(self.window, self.db_path, username)
        dialog.window.wait_window()

    def _excluir_usuario(self):
        """Exclui usuário"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Atenção", "Selecione um usuário")
            return

        username = self.tree.item(selection[0])['values'][0]

        if username == self.user_session['username']:
            messagebox.showerror("Erro", "Não é possível excluir o próprio usuário")
            return

        if messagebox.askyesno("Confirmar Exclusão",
                              f"Tem certeza que deseja excluir o usuário {username}?\n\nEsta ação não pode ser desfeita!"):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM usuarios WHERE username = ?", (username,))
            conn.commit()
            conn.close()

            self._load_users()
            messagebox.showinfo("Sucesso", "Usuário excluído com sucesso")

    def _center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

class UserDialog:
    def __init__(self, parent, db_path, user_session, username=None, on_save_callback=None):
        self.parent = parent
        self.db_path = db_path
        self.user_session = user_session
        self.username = username
        self.on_save_callback = on_save_callback
        self.is_edit = username is not None

        self.window = tk.Toplevel(parent)
        self.window.title("Editar Usuário" if self.is_edit else "Novo Usuário")
        self.window.geometry("400x300")
        self.window.resizable(False, False)
        self.window.grab_set()

        self._create_interface()
        if self.is_edit:
            self._load_user_data()
        self._center_window()

    def _create_interface(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Campos
        ttk.Label(main_frame, text="Usuário:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(main_frame, width=30)
        self.username_entry.grid(row=0, column=1, pady=5, padx=(10, 0))

        ttk.Label(main_frame, text="Nome Completo:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.nome_entry = ttk.Entry(main_frame, width=30)
        self.nome_entry.grid(row=1, column=1, pady=5, padx=(10, 0))

        ttk.Label(main_frame, text="Email:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.email_entry = ttk.Entry(main_frame, width=30)
        self.email_entry.grid(row=2, column=1, pady=5, padx=(10, 0))

        ttk.Label(main_frame, text="Perfil:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.perfil_var = tk.StringVar()
        self.perfil_combo = ttk.Combobox(
            main_frame,
            textvariable=self.perfil_var,
            values=['atendente', 'gestor', 'admin'],
            state='readonly',
            width=27
        )
        self.perfil_combo.grid(row=3, column=1, pady=5, padx=(10, 0))
        self.perfil_combo.set('atendente')

        if not self.is_edit:
            ttk.Label(main_frame, text="Senha:").grid(row=4, column=0, sticky=tk.W, pady=5)
            self.senha_entry = ttk.Entry(main_frame, width=30, show="*")
            self.senha_entry.grid(row=4, column=1, pady=5, padx=(10, 0))

        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=(20, 0))

        ttk.Button(
            btn_frame,
            text="Salvar",
            command=self._salvar
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Cancelar",
            command=self.window.destroy
        ).pack(side=tk.RIGHT, padx=5)

    def _load_user_data(self):
        """Carrega dados do usuário para edição"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT username, nome_completo, email, perfil
            FROM usuarios WHERE username = ?
        """, (self.username,))

        row = cursor.fetchone()
        conn.close()

        if row:
            self.username_entry.insert(0, row[0])
            self.username_entry.config(state='disabled')  # Não permitir alterar username
            self.nome_entry.insert(0, row[1] or '')
            self.email_entry.insert(0, row[2] or '')
            self.perfil_var.set(row[3])

    def _salvar(self):
        """Salva usuário"""
        username = self.username_entry.get().strip()
        nome = self.nome_entry.get().strip()
        email = self.email_entry.get().strip()
        perfil = self.perfil_var.get()

        if not username or not nome:
            messagebox.showerror("Erro", "Usuário e nome são obrigatórios")
            return

        try:
            from backend.auth import AuthManager
            auth = AuthManager(self.db_path)

            if self.is_edit:
                # Para edição, não alterar senha
                conn = sqlite3.connect(self.db_path, timeout=10)
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE usuarios
                    SET nome_completo = ?, email = ?, perfil = ?
                    WHERE username = ?
                """, (nome, email, perfil, username))
                conn.commit()
                conn.close()
                messagebox.showinfo("Sucesso", "Usuário atualizado com sucesso!")
            else:
                # Novo usuário
                senha = self.senha_entry.get()
                if not senha:
                    messagebox.showerror("Erro", "Senha é obrigatória")
                    return

                result = auth.criar_usuario(
                    username=username,
                    password=senha,
                    nome_completo=nome,
                    email=email,
                    perfil=perfil,
                    criado_por=self.user_session['user_id']
                )

                if result['success']:
                    messagebox.showinfo("Sucesso", "Usuário criado com sucesso!")
                else:
                    messagebox.showerror("Erro", result['message'])
                    return

            self.window.destroy()
            if self.on_save_callback:
                self.on_save_callback()

        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                messagebox.showerror("Erro", "Banco de dados ocupado. Tente novamente em alguns segundos.")
            else:
                messagebox.showerror("Erro", f"Erro de banco: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")
        finally:
            if conn:
                conn.close()

    def _center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

class PasswordDialog:
    def __init__(self, parent, db_path, username):
        self.parent = parent
        self.db_path = db_path
        self.username = username

        self.window = tk.Toplevel(parent)
        self.window.title(f"Alterar Senha - {username}")
        self.window.geometry("300x150")
        self.window.resizable(False, False)
        self.window.grab_set()

        self._create_interface()
        self._center_window()

    def _create_interface(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Nova Senha:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.senha_entry = ttk.Entry(main_frame, width=25, show="*")
        self.senha_entry.grid(row=0, column=1, pady=5, padx=(10, 0))

        ttk.Label(main_frame, text="Confirmar:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.confirm_entry = ttk.Entry(main_frame, width=25, show="*")
        self.confirm_entry.grid(row=1, column=1, pady=5, padx=(10, 0))

        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(20, 0))

        ttk.Button(
            btn_frame,
            text="Alterar",
            command=self._alterar
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Cancelar",
            command=self.window.destroy
        ).pack(side=tk.RIGHT, padx=5)

    def _alterar(self):
        """Altera senha"""
        senha = self.senha_entry.get()
        confirm = self.confirm_entry.get()

        if not senha:
            messagebox.showerror("Erro", "Digite a nova senha")
            return

        if senha != confirm:
            messagebox.showerror("Erro", "Senhas não coincidem")
            return

        try:
            from backend.auth import AuthManager
            auth = AuthManager(self.db_path)

            # Gerar novo hash
            hashed = auth.hash_password(senha)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE usuarios SET senha_hash = ? WHERE username = ?",
                (hashed, self.username)
            )
            conn.commit()
            conn.close()

            messagebox.showinfo("Sucesso", "Senha alterada com sucesso!")
            self.window.destroy()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao alterar senha: {str(e)}")

    def _center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

class SettingsDialog:
    def __init__(self, parent, db_path, user_session):
        self.parent = parent
        self.db_path = db_path
        self.user_session = user_session

        self.window = tk.Toplevel(parent)
        self.window.title("Configurações do Sistema")
        self.window.geometry("500x500")
        self.window.resizable(False, False)
        self.window.grab_set()

        self._create_interface()
        self._load_settings()
        self._center_window()

    def _create_interface(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        ttk.Label(
            main_frame,
            text="Configurações do Sistema",
            font=('Arial', 14, 'bold')
        ).pack(pady=(0, 20))

        # Notebook para abas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Aba Geral
        geral_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(geral_frame, text="Geral")

        ttk.Label(geral_frame, text="Nome da Clínica:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.nome_clinica = ttk.Entry(geral_frame, width=40)
        self.nome_clinica.grid(row=0, column=1, pady=5, padx=(10, 0))

        ttk.Label(geral_frame, text="Telefone da Clínica:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.telefone_clinica = ttk.Entry(geral_frame, width=40)
        self.telefone_clinica.grid(row=1, column=1, pady=5, padx=(10, 0))

        # Aba Backup
        backup_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(backup_frame, text="Backup")

        self.backup_auto = tk.BooleanVar()
        ttk.Checkbutton(
            backup_frame,
            text="Ativar backup automático",
            variable=self.backup_auto
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)

        ttk.Label(backup_frame, text="Horário do Backup:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.backup_hora = ttk.Entry(backup_frame, width=20)
        self.backup_hora.grid(row=1, column=1, pady=5, padx=(10, 0))

        ttk.Label(backup_frame, text="Dias de Retenção:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.backup_retencao = ttk.Entry(backup_frame, width=20)
        self.backup_retencao.grid(row=2, column=1, pady=5, padx=(10, 0))

        # Aba Limites
        limites_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(limites_frame, text="Limites")

        ttk.Label(limites_frame, text="Máx. contatos/dia:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.max_contatos_dia = ttk.Entry(limites_frame, width=20)
        self.max_contatos_dia.grid(row=0, column=1, pady=5, padx=(10, 0))

        ttk.Label(limites_frame, text="Intervalo mínimo (seg):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.intervalo_minimo = ttk.Entry(limites_frame, width=20)
        self.intervalo_minimo.grid(row=1, column=1, pady=5, padx=(10, 0))

        ttk.Label(limites_frame, text="Máx. tentativas/paciente:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.max_tentativas = ttk.Entry(limites_frame, width=20)
        self.max_tentativas.grid(row=2, column=1, pady=5, padx=(10, 0))

        self.trabalha_24h = tk.BooleanVar()
        ttk.Checkbutton(
            limites_frame,
            text="Clínica trabalha 24 horas por dia",
            variable=self.trabalha_24h,
            command=self._toggle_horarios
        ).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)

        ttk.Label(limites_frame, text="Horário início (hora, ex: 8):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.horario_inicio = ttk.Entry(limites_frame, width=20)
        self.horario_inicio.grid(row=4, column=1, pady=5, padx=(10, 0))

        ttk.Label(limites_frame, text="Horário fim (hora, ex: 20):").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.horario_fim = ttk.Entry(limites_frame, width=20)
        self.horario_fim.grid(row=5, column=1, pady=5, padx=(10, 0))

        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))

        ttk.Button(
            btn_frame,
            text="Salvar",
            command=self._salvar
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Cancelar",
            command=self.window.destroy
        ).pack(side=tk.RIGHT, padx=5)

    def _load_settings(self):
        """Carrega configurações atuais"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Configurações gerais
        cursor.execute("SELECT chave, valor FROM configuracoes")
        configs = dict(cursor.fetchall())

        self.nome_clinica.insert(0, configs.get('nome_clinica', 'Clínica Exemplo'))
        self.telefone_clinica.insert(0, configs.get('telefone_clinica', ''))

        backup_auto = configs.get('backup_automatico', 'true').lower() == 'true'
        self.backup_auto.set(backup_auto)
        self.backup_hora.insert(0, configs.get('backup_hora', '23:00'))
        self.backup_retencao.insert(0, configs.get('dias_retencao_backup', '7'))

        # Limites
        cursor.execute("SELECT tipo_limite, valor_limite FROM limites_sistema")
        limites = dict(cursor.fetchall())

        self.max_contatos_dia.insert(0, str(limites.get('max_primeiros_contatos_dia', 30)))
        self.intervalo_minimo.insert(0, str(limites.get('intervalo_minimo_segundos', 120)))
        self.max_tentativas.insert(0, str(limites.get('max_tentativas_paciente', 3)))
        self.horario_inicio.insert(0, str(limites.get('horario_inicio', 8)))
        self.horario_fim.insert(0, str(limites.get('horario_fim', 20)))

        # Carregar configuração 24h
        trabalha_24h = configs.get('trabalha_24h', 'false').lower() == 'true'
        self.trabalha_24h.set(trabalha_24h)
        self._toggle_horarios()

        conn.close()

    def _salvar(self):
        """Salva configurações"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()

            # Configurações gerais
            configs = [
                ('nome_clinica', self.nome_clinica.get()),
                ('telefone_clinica', self.telefone_clinica.get()),
                ('backup_automatico', 'true' if self.backup_auto.get() else 'false'),
                ('backup_hora', self.backup_hora.get()),
                ('dias_retencao_backup', self.backup_retencao.get()),
            ]

            # Adicionar configuração 24h
            configs.append(('trabalha_24h', 'true' if self.trabalha_24h.get() else 'false'))

            for chave, valor in configs:
                cursor.execute("""
                    INSERT OR REPLACE INTO configuracoes (chave, valor, tipo, descricao)
                    VALUES (?, ?, 'string', '')
                """, (chave, valor))

            # Limites
            try:
                limites = [
                    ('max_primeiros_contatos_dia', int(self.max_contatos_dia.get())),
                    ('intervalo_minimo_segundos', int(self.intervalo_minimo.get())),
                    ('max_tentativas_paciente', int(self.max_tentativas.get())),
                    ('horario_inicio', int(self.horario_inicio.get())),
                    ('horario_fim', int(self.horario_fim.get())),
                ]
            except ValueError as e:
                messagebox.showerror("Erro", f"Valores numéricos inválidos: {str(e)}")
                return

            for tipo, valor in limites:
                cursor.execute("""
                    UPDATE limites_sistema
                    SET valor_limite = ?
                    WHERE tipo_limite = ?
                """, (valor, tipo))

            conn.commit()
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
            self.window.destroy()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar configurações: {str(e)}")
        finally:
            if conn:
                conn.close()

    def _toggle_horarios(self):
        """Ativa/desativa campos de horário baseado na opção 24h"""
        if self.trabalha_24h.get():
            # Desabilitar campos de horário
            self.horario_inicio.config(state='disabled')
            self.horario_fim.config(state='disabled')
        else:
            # Habilitar campos de horário
            self.horario_inicio.config(state='normal')
            self.horario_fim.config(state='normal')

    def _center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

class RescheduleDialog:
    def __init__(self, parent, db_path, paciente_id, on_rescheduled=None):
        self.parent = parent
        self.db_path = db_path
        self.paciente_id = paciente_id
        self.on_rescheduled = on_rescheduled

        self.window = tk.Toplevel(parent)
        self.window.title("Reagendar Consulta")
        self.window.geometry("400x350")
        self.window.resizable(False, False)
        self.window.grab_set()

        self._load_current_data()
        self._create_interface()
        self._center_window()

    def _load_current_data(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT nome, data_consulta, hora_consulta
            FROM pacientes
            WHERE id = ?
        """, (self.paciente_id,))

        result = cursor.fetchone()
        conn.close()

        if result:
            self.paciente_nome = result[0]
            self.data_atual = result[1] or ''
            self.hora_atual = result[2] or ''
        else:
            self.paciente_nome = "Desconhecido"
            self.data_atual = ''
            self.hora_atual = ''

    def _create_interface(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        ttk.Label(
            main_frame,
            text=f"Reagendar Consulta - {self.paciente_nome}",
            font=('Arial', 12, 'bold')
        ).pack(pady=(0, 10))

        # Dados atuais
        current_frame = ttk.LabelFrame(main_frame, text="Dados Atuais", padding="10")
        current_frame.pack(fill=tk.X, pady=(0, 10))

        hora_atual_formatada = str(self.hora_atual)[:5] if self.hora_atual else ''
        ttk.Label(current_frame, text=f"Data: {self.data_atual}").pack(anchor=tk.W)
        ttk.Label(current_frame, text=f"Hora: {hora_atual_formatada}").pack(anchor=tk.W)

        # Novos dados
        new_frame = ttk.LabelFrame(main_frame, text="Novos Dados", padding="10")
        new_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(new_frame, text="Nova Data (DD/MM/YYYY):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.nova_data = ttk.Entry(new_frame, width=15)
        self.nova_data.grid(row=0, column=1, pady=5, padx=(10, 0))

        ttk.Label(new_frame, text="Nova Hora (HH:MM):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.nova_hora = ttk.Entry(new_frame, width=15)
        self.nova_hora.grid(row=1, column=1, pady=5, padx=(10, 0))

        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="Reagendar",
            command=self._reagendar
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Cancelar",
            command=self.window.destroy
        ).pack(side=tk.RIGHT, padx=5)

    def _reagendar(self):
        nova_data = self.nova_data.get().strip()
        nova_hora = self.nova_hora.get().strip()

        if not nova_data or not nova_hora:
            messagebox.showerror("Erro", "Data e hora são obrigatórios")
            return

        # Validar formato
        try:
            from datetime import datetime
            datetime.strptime(nova_data, '%d/%m/%Y')
            datetime.strptime(nova_hora, '%H:%M')
        except ValueError:
            messagebox.showerror("Erro", "Formato inválido. Use DD/MM/YYYY para data e HH:MM para hora")
            return

        # Confirmar
        if not messagebox.askyesno(
            "Confirmar Reagendamento",
            f"Reagendar consulta para {nova_data} às {nova_hora}?"
        ):
            return

        # Atualizar no banco
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE pacientes
                SET data_consulta = ?, hora_consulta = ?, status = 'reagendado'
                WHERE id = ?
            """, (nova_data, nova_hora, self.paciente_id))

            conn.commit()
            conn.close()

            messagebox.showinfo("Sucesso", "Consulta reagendada com sucesso!")
            self.window.destroy()

            if self.on_rescheduled:
                self.on_rescheduled()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao reagendar: {str(e)}")

    def _center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

class MessageManagementDialog:
    def __init__(self, parent, db_path, user_session):
        self.parent = parent
        self.db_path = db_path
        self.user_session = user_session

        self.window = tk.Toplevel(parent)
        self.window.title("Gerenciamento de Mensagens")
        self.window.geometry("900x600")
        self.window.resizable(True, True)
        self.window.grab_set()

        self._create_interface()
        self._load_messages()
        self._center_window()

    def _create_interface(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        ttk.Label(
            main_frame,
            text="Gerenciamento de Mensagens do Sistema",
            font=('Arial', 14, 'bold')
        ).pack(pady=(0, 20))

        # Lista de mensagens
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Treeview
        columns = ('tipo', 'texto', 'categoria', 'tom', 'ativo', 'data_criacao')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        self.tree.heading('tipo', text='Tipo')
        self.tree.heading('texto', text='Texto da Mensagem')
        self.tree.heading('categoria', text='Categoria')
        self.tree.heading('tom', text='Tom')
        self.tree.heading('ativo', text='Ativo')
        self.tree.heading('data_criacao', text='Data Criação')

        self.tree.column('tipo', width=100)
        self.tree.column('texto', width=400)
        self.tree.column('categoria', width=100)
        self.tree.column('tom', width=80)
        self.tree.column('ativo', width=60)
        self.tree.column('data_criacao', width=120)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Button(
            btn_frame,
            text="➕ Nova Mensagem",
            command=self._nova_mensagem
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="✏️ Editar",
            command=self._editar_mensagem
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="🗑️ Excluir",
            command=self._excluir_mensagem
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="🔄 Ativar/Desativar",
            command=self._toggle_ativo
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="🔄 Atualizar Lista",
            command=self._load_messages
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            btn_frame,
            text="Fechar",
            command=self.window.destroy
        ).pack(side=tk.RIGHT, padx=5)

    def _load_messages(self):
        """Carrega lista de mensagens"""
        # Limpar lista
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = sqlite3.connect(self.db_path, timeout=10)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, tipo, texto, categoria, tom, usa_emoji, ativo, data_criacao
            FROM mensagens
            ORDER BY tipo, data_criacao DESC
        """)

        for row in cursor.fetchall():
            mid, tipo, texto, categoria, tom, usa_emoji, ativo, data_criacao = row
            ativo_str = "Sim" if ativo else "Não"
            data_str = data_criacao[:10] if data_criacao else ""

            # Truncar texto para exibição
            texto_display = texto[:100] + "..." if len(texto) > 100 else texto

            self.tree.insert('', tk.END, values=(tipo, texto_display, categoria or '', tom or '', ativo_str, data_str), tags=(str(mid),))

        conn.close()

    def _nova_mensagem(self):
        """Cria nova mensagem"""
        dialog = MessageDialog(self.window, self.db_path, self.user_session, on_save_callback=self._load_messages)
        dialog.window.wait_window()

    def _editar_mensagem(self):
        """Edita mensagem selecionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Atenção", "Selecione uma mensagem")
            return

        item = selection[0]
        tags = self.tree.item(item, 'tags')
        mensagem_id = int(tags[0]) if tags else None

        if mensagem_id:
            dialog = MessageDialog(self.window, self.db_path, self.user_session, mensagem_id=mensagem_id, on_save_callback=self._load_messages)
            dialog.window.wait_window()

    def _excluir_mensagem(self):
        """Exclui mensagem selecionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Atenção", "Selecione uma mensagem")
            return

        item = selection[0]
        tags = self.tree.item(item, 'tags')
        mensagem_id = int(tags[0]) if tags else None

        if not mensagem_id:
            return

        if messagebox.askyesno("Confirmar Exclusão",
                              "Tem certeza que deseja excluir esta mensagem?\n\nEsta ação não pode ser desfeita!"):
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM mensagens WHERE id = ?", (mensagem_id,))
            conn.commit()
            conn.close()

            self._load_messages()
            messagebox.showinfo("Sucesso", "Mensagem excluída com sucesso")

    def _toggle_ativo(self):
        """Ativa/desativa mensagem"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Atenção", "Selecione uma mensagem")
            return

        item = selection[0]
        tags = self.tree.item(item, 'tags')
        mensagem_id = int(tags[0]) if tags else None

        if not mensagem_id:
            return

        conn = sqlite3.connect(self.db_path, timeout=10)
        cursor = conn.cursor()

        cursor.execute("SELECT ativo FROM mensagens WHERE id = ?", (mensagem_id,))
        ativo_atual = cursor.fetchone()[0]

        cursor.execute(
            "UPDATE mensagens SET ativo = ? WHERE id = ?",
            (0 if ativo_atual else 1, mensagem_id)
        )

        conn.commit()
        conn.close()

        self._load_messages()
        status = "desativada" if ativo_atual else "ativada"
        messagebox.showinfo("Sucesso", f"Mensagem {status} com sucesso")

    def _center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

class MessageDialog:
    def __init__(self, parent, db_path, user_session, mensagem_id=None, on_save_callback=None):
        self.parent = parent
        self.db_path = db_path
        self.user_session = user_session
        self.mensagem_id = mensagem_id
        self.on_save_callback = on_save_callback
        self.is_edit = mensagem_id is not None

        self.window = tk.Toplevel(parent)
        self.window.title("Editar Mensagem" if self.is_edit else "Nova Mensagem")
        self.window.geometry("600x400")
        self.window.resizable(False, False)
        self.window.grab_set()

        self._create_interface()
        if self.is_edit:
            self._load_message_data()
        self._center_window()

    def _create_interface(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        ttk.Label(
            main_frame,
            text="Editar Mensagem" if self.is_edit else "Nova Mensagem",
            font=('Arial', 12, 'bold')
        ).pack(pady=(0, 10))

        # Campos
        ttk.Label(main_frame, text="Tipo:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.tipo_var = tk.StringVar()
        self.tipo_combo = ttk.Combobox(
            main_frame,
            textvariable=self.tipo_var,
            values=['primeiro_contato', 'confirmacao', 'lembrete', 'reagendamento', 'follow_up'],
            state='readonly'
        )
        self.tipo_combo.grid(row=0, column=1, pady=5, padx=(10, 0), sticky=(tk.W, tk.E))
        self.tipo_combo.set('primeiro_contato')

        ttk.Label(main_frame, text="Categoria:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.categoria_entry = ttk.Entry(main_frame, width=30)
        self.categoria_entry.grid(row=1, column=1, pady=5, padx=(10, 0), sticky=(tk.W, tk.E))

        ttk.Label(main_frame, text="Tom:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.tom_var = tk.StringVar()
        self.tom_combo = ttk.Combobox(
            main_frame,
            textvariable=self.tom_var,
            values=['formal', 'amigavel', 'neutro'],
            state='readonly'
        )
        self.tom_combo.grid(row=2, column=1, pady=5, padx=(10, 0), sticky=(tk.W, tk.E))
        self.tom_combo.set('neutro')

        ttk.Label(main_frame, text="Texto da Mensagem:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.texto_text = tk.Text(main_frame, height=8, wrap=tk.WORD)
        self.texto_text.grid(row=3, column=1, pady=5, padx=(10, 0), sticky=(tk.W, tk.E))

        self.usa_emoji_var = tk.BooleanVar()
        ttk.Checkbutton(
            main_frame,
            text="Usa emoji",
            variable=self.usa_emoji_var
        ).grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=(20, 0), sticky=(tk.W, tk.E))

        ttk.Button(
            btn_frame,
            text="Salvar",
            command=self._salvar
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Cancelar",
            command=self.window.destroy
        ).pack(side=tk.RIGHT, padx=5)

        main_frame.columnconfigure(1, weight=1)

    def _load_message_data(self):
        """Carrega dados da mensagem para edição"""
        conn = sqlite3.connect(self.db_path, timeout=10)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT tipo, texto, categoria, tom, usa_emoji
            FROM mensagens WHERE id = ?
        """, (self.mensagem_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            tipo, texto, categoria, tom, usa_emoji = row
            self.tipo_var.set(tipo)
            self.texto_text.insert(1.0, texto)
            self.categoria_entry.insert(0, categoria or '')
            self.tom_var.set(tom or 'neutro')
            self.usa_emoji_var.set(bool(usa_emoji))

    def _salvar(self):
        """Salva mensagem"""
        tipo = self.tipo_var.get()
        texto = self.texto_text.get(1.0, tk.END).strip()
        categoria = self.categoria_entry.get().strip()
        tom = self.tom_var.get()
        usa_emoji = 1 if self.usa_emoji_var.get() else 0

        if not texto:
            messagebox.showerror("Erro", "Texto da mensagem é obrigatório")
            return

        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()

            if self.is_edit:
                cursor.execute("""
                    UPDATE mensagens
                    SET tipo = ?, texto = ?, categoria = ?, tom = ?, usa_emoji = ?
                    WHERE id = ?
                """, (tipo, texto, categoria or None, tom, usa_emoji, self.mensagem_id))
                messagebox.showinfo("Sucesso", "Mensagem atualizada com sucesso!")
            else:
                cursor.execute("""
                    INSERT INTO mensagens (tipo, texto, categoria, tom, usa_emoji, ativo)
                    VALUES (?, ?, ?, ?, ?, 1)
                """, (tipo, texto, categoria or None, tom, usa_emoji))
                messagebox.showinfo("Sucesso", "Mensagem criada com sucesso!")

            conn.commit()
            conn.close()

            self.window.destroy()
            if self.on_save_callback:
                self.on_save_callback()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")

    def _center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

class ImportDialog:
    def __init__(self, parent, db_path, user_session, on_import_callback=None):
        self.parent = parent
        self.db_path = db_path
        self.user_session = user_session
        self.on_import_callback = on_import_callback
        self.security = SecurityValidator(db_path)

        self.window = tk.Toplevel(parent)
        self.window.title("Importar Planilha de Pacientes")
        self.window.geometry("700x500")
        self.window.resizable(False, False)
        self.window.grab_set()

        self._create_interface()
        self._center_window()

    def _create_interface(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        ttk.Label(
            main_frame,
            text="Importar Planilha de Pacientes",
            font=('Arial', 14, 'bold')
        ).grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)

        # Instruções (mais compactas)
        instr_frame = ttk.LabelFrame(main_frame, text="Instruções", padding="5")
        instr_frame.grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))

        instr_text = "Colunas obrigatórias: nome, telefone\nOpcionais: email, data_nascimento, cpf, data_consulta, hora_consulta, tipo_consulta, profissional, observacoes, consentimento_whatsapp\nFormatos: .xlsx, .xls, .csv"

        ttk.Label(
            instr_frame,
            text=instr_text,
            justify=tk.LEFT,
            font=('Arial', 8)
        ).pack(anchor=tk.W)

        # Seleção de arquivo
        ttk.Label(main_frame, text="Arquivo:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.file_path_var = tk.StringVar()
        ttk.Entry(
            main_frame,
            textvariable=self.file_path_var,
            width=40,
            state='readonly'
        ).grid(row=2, column=1, pady=5, sticky=(tk.W, tk.E))

        # Botões de arquivo
        file_btn_frame = ttk.Frame(main_frame)
        file_btn_frame.grid(row=3, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))

        ttk.Button(
            file_btn_frame,
            text="📥 Baixar Modelo",
            command=self._baixar_modelo
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            file_btn_frame,
            text="Selecionar Arquivo",
            command=self._selecionar_arquivo
        ).pack(side=tk.LEFT, padx=(0, 5))

        # Opções de importação
        options_frame = ttk.LabelFrame(main_frame, text="Opções", padding="5")
        options_frame.grid(row=4, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))

        self.skip_duplicates_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Pular duplicatas (telefone)",
            variable=self.skip_duplicates_var
        ).pack(anchor=tk.W)

        # Progresso
        self.progress_var = tk.StringVar(value="")
        ttk.Label(
            main_frame,
            textvariable=self.progress_var,
            font=('Arial', 8)
        ).grid(row=5, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)

        # Botões principais
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=(10, 0), sticky=(tk.W, tk.E))

        ttk.Button(
            btn_frame,
            text="📤 Importar Planilha",
            command=self._importar
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Cancelar",
            command=self.window.destroy
        ).pack(side=tk.RIGHT, padx=5)

        # Configurar grid
        main_frame.columnconfigure(1, weight=1)

    def _baixar_modelo(self):
        """Baixa um arquivo Excel modelo com as colunas necessárias"""
        try:
            # Criar DataFrame modelo com uma linha de exemplo
            import pandas as pd

            modelo_data = {
                'nome': ['João Silva'],
                'telefone': ['11999999999'],
                'email': ['joao@email.com'],
                'data_nascimento': ['15/05/1980'],
                'cpf': ['12345678901'],
                'data_consulta': ['25/12/2025'],
                'hora_consulta': ['14:30'],
                'tipo_consulta': ['Consulta de rotina'],
                'profissional': ['Dr. Maria Santos'],
                'observacoes': ['Paciente com histórico de hipertensão'],
                'consentimento_whatsapp': ['SIM']
            }

            df_modelo = pd.DataFrame(modelo_data)

            # Selecionar local para salvar
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                title="Salvar Modelo de Planilha",
                initialfile="modelo_pacientes.xlsx"
            )

            if filename:
                df_modelo.to_excel(filename, index=False)
                messagebox.showinfo("Sucesso", f"Modelo salvo em:\n{filename}\n\nPreencha os dados e importe usando 'Selecionar Arquivo'.")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar modelo: {str(e)}")

    def _selecionar_arquivo(self):
        filetypes = [
            ('Excel files', '*.xlsx *.xls'),
            ('CSV files', '*.csv'),
            ('All files', '*.*')
        ]

        filename = filedialog.askopenfilename(
            title="Selecionar arquivo de pacientes",
            filetypes=filetypes
        )

        if filename:
            self.file_path_var.set(filename)

    def _importar(self):
        arquivo = self.file_path_var.get()
        if not arquivo:
            messagebox.showerror("Erro", "Selecione um arquivo primeiro")
            return

        if not os.path.exists(arquivo):
            messagebox.showerror("Erro", "Arquivo não encontrado")
            return

        try:
            # Ler arquivo
            if arquivo.endswith('.csv'):
                df = pd.read_csv(arquivo)
            else:
                df = pd.read_excel(arquivo)

            self.progress_var.set("Lendo arquivo...")

            # Validar colunas obrigatórias
            colunas_obrigatorias = ['nome', 'telefone']
            colunas_faltando = [col for col in colunas_obrigatorias if col not in df.columns]

            if colunas_faltando:
                messagebox.showerror(
                    "Erro",
                    f"Colunas obrigatórias faltando: {', '.join(colunas_faltando)}"
                )
                return

            # Processar dados
            total = len(df)
            importados = 0
            erros = 0
            duplicados = 0

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for idx, row in df.iterrows():
                try:
                    self.progress_var.set(f"Processando {idx + 1}/{total}...")

                    # Extrair dados
                    dados = {
                        'nome': str(row.get('nome', '')).strip(),
                        'telefone': str(row.get('telefone', '')).strip(),
                        'email': str(row.get('email', '')).strip() if pd.notna(row.get('email')) else '',
                        'data_nascimento': str(row.get('data_nascimento', '')).strip() if pd.notna(row.get('data_nascimento')) else '',
                        'cpf': str(row.get('cpf', '')).strip() if pd.notna(row.get('cpf')) else '',
                        'data_consulta': str(row.get('data_consulta', '')).strip() if pd.notna(row.get('data_consulta')) else '',
                        'hora_consulta': str(row.get('hora_consulta', '')).strip() if pd.notna(row.get('hora_consulta')) else '',
                        'tipo_consulta': str(row.get('tipo_consulta', '')).strip() if pd.notna(row.get('tipo_consulta')) else '',
                        'profissional': str(row.get('profissional', '')).strip() if pd.notna(row.get('profissional')) else '',
                        'observacoes': str(row.get('observacoes', '')).strip() if pd.notna(row.get('observacoes')) else '',
                    }

                    # Verificar consentimento
                    consentimento_str = str(row.get('consentimento_whatsapp', '')).strip().upper()
                    consentimento = consentimento_str in ['SIM', 'S', 'YES', 'Y', '1', 'TRUE']

                    # Validações básicas
                    if not dados['nome']:
                        erros += 1
                        continue

                    if not dados['telefone']:
                        erros += 1
                        continue

                    # Validar telefone
                    valido, telefone_formatado, erro = self.security.validar_telefone(dados['telefone'])
                    if not valido:
                        erros += 1
                        continue

                    # Validar datas se fornecidas
                    try:
                        from datetime import datetime
                        if dados['data_nascimento']:
                            datetime.strptime(dados['data_nascimento'], '%d/%m/%Y')
                        if dados['data_consulta']:
                            datetime.strptime(dados['data_consulta'], '%d/%m/%Y')
                    except ValueError:
                        erros += 1
                        continue

                    # Validar email se fornecido
                    if dados['email']:
                        valido, erro = self.security.validar_email(dados['email'])
                        if not valido:
                            erros += 1
                            continue

                    # Validar CPF se fornecido
                    if dados['cpf']:
                        valido, erro = self.security.validar_cpf(dados['cpf'])
                        if not valido:
                            erros += 1
                            continue

                    # Verificar duplicatas se opção ativada
                    if self.skip_duplicates_var.get():
                        cursor.execute("SELECT id FROM pacientes WHERE telefone = ?", (dados['telefone'],))
                        if cursor.fetchone():
                            duplicados += 1
                            continue

                    # Inserir paciente
                    cursor.execute("""
                        INSERT INTO pacientes (
                            nome, telefone, telefone_formatado, email, data_nascimento, cpf,
                            data_consulta, hora_consulta, tipo_consulta, profissional, observacoes,
                            cadastrado_por, data_cadastro
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        dados['nome'],
                        dados['telefone'],
                        telefone_formatado,
                        dados['email'] or None,
                        dados['data_nascimento'] or None,
                        dados['cpf'] or None,
                        dados['data_consulta'] or None,
                        dados['hora_consulta'] or None,
                        dados['tipo_consulta'] or None,
                        dados['profissional'] or None,
                        dados['observacoes'] or None,
                        self.user_session['user_id'],
                        datetime.now()
                    ))

                    paciente_id = cursor.lastrowid

                    # Registrar consentimento se fornecido
                    if consentimento:
                        lgpd = LGPDManager(self.db_path)
                        lgpd.registrar_consentimento(
                            paciente_id,
                            'planilha',
                            self.user_session['user_id'],
                            'Consentimento informado na planilha de importação'
                        )

                    importados += 1

                except Exception as e:
                    erros += 1
                    continue

            conn.commit()
            conn.close()

            # Resultado
            msg = f"Importação concluída!\n\n"
            msg += f"Total de registros: {total}\n"
            msg += f"Importados: {importados}\n"
            msg += f"Duplicados pulados: {duplicados}\n"
            msg += f"Erros: {erros}"

            messagebox.showinfo("Importação Concluída", msg)
            self.window.destroy()

            if self.on_import_callback:
                self.on_import_callback()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro durante importação: {str(e)}")

    def _center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')