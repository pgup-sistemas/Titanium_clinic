import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date

class PatientView:
    def __init__(self, parent, db_path: str, user_session: dict, on_preparar_mensagem):
        self.db_path = db_path
        self.user_session = user_session
        self.on_preparar_mensagem = on_preparar_mensagem
        
        self.frame = ttk.Frame(parent)
        self._criar_interface()
        self.atualizar_lista()
    
    def _criar_interface(self):
        # Toolbar superior
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill=tk.X, padx=10, pady=10)
        
        # Filtros
        ttk.Label(toolbar, text="Filtrar por status:").pack(side=tk.LEFT, padx=5)

        self.filtro_status = ttk.Combobox(
            toolbar,
            values=['Todos', 'Pendente', 'Mensagem Preparada', 'Enviada', 'Confirmado', 'Sem Resposta', 'Reagendado'],
            state='readonly',
            width=20
        )
        self.filtro_status.set('Todos')
        self.filtro_status.pack(side=tk.LEFT, padx=5)
        self.filtro_status.bind('<<ComboboxSelected>>', lambda e: self.atualizar_lista())

        # Checkbox para mostrar todos os pacientes
        self.mostrar_todos_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            toolbar,
            text="Mostrar Todos",
            variable=self.mostrar_todos_var,
            command=self.atualizar_lista
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            toolbar,
            text="🔄 Atualizar",
            command=self.atualizar_lista
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            toolbar,
            text="📊 Importar Planilha",
            command=self._importar_planilha
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            toolbar,
            text="➕ Novo Paciente",
            command=self._novo_paciente
        ).pack(side=tk.RIGHT, padx=5)
        
        # Tabela de pacientes
        table_frame = ttk.Frame(self.frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Scrollbars
        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        
        # Treeview
        self.tree = ttk.Treeview(
            table_frame,
            columns=('nome', 'telefone', 'data', 'hora', 'status', 'tentativas'),
            show='headings',
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set
        )
        
        # Configurar colunas
        self.tree.heading('nome', text='Nome')
        self.tree.heading('telefone', text='Telefone')
        self.tree.heading('data', text='Data')
        self.tree.heading('hora', text='Hora')
        self.tree.heading('status', text='Status')
        self.tree.heading('tentativas', text='Tentativas')
        
        self.tree.column('nome', width=200)
        self.tree.column('telefone', width=120)
        self.tree.column('data', width=100)
        self.tree.column('hora', width=80)
        self.tree.column('status', width=150)
        self.tree.column('tentativas', width=80, anchor=tk.CENTER)
        
        # Posicionar scrollbars
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)
        
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind duplo clique
        self.tree.bind('<Double-1>', self._on_double_click)
        
        # Menu de contexto (botão direito)
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="✉️ Preparar Mensagem", command=self._preparar_mensagem_selecionado)
        self.context_menu.add_command(label="✅ Marcar como Confirmado", command=self._marcar_confirmado)
        self.context_menu.add_command(label="🔄 Reagendar", command=self._reagendar)
        self.context_menu.add_command(label="↩️ Reverter Reagendamento", command=self._reverter_reagendamento)
        self.context_menu.add_command(label="❌ Sem Resposta", command=self._marcar_sem_resposta)
        self.context_menu.add_command(label="📝 Alterar Status", command=self._alterar_status)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ Excluir", command=self._excluir_paciente)
        
        self.tree.bind('<Button-3>', self._show_context_menu)
        
        # Frame de ações
        actions_frame = ttk.Frame(self.frame)
        actions_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(
            actions_frame,
            text="📱 Preparar Mensagem",
            command=self._preparar_mensagem_selecionado
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            actions_frame,
            text="✅ Marcar Confirmado",
            command=self._marcar_confirmado
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            actions_frame,
            text="🔄 Reagendar",
            command=self._reagendar
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            actions_frame,
            text="↩️ Reverter Reagendamento",
            command=self._reverter_reagendamento
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            actions_frame,
            text="📊 WhatsApp Web",
            command=self._abrir_whatsapp
        ).pack(side=tk.RIGHT, padx=5)
    
    def atualizar_lista(self):
        """Atualiza lista de pacientes"""
        # Limpar tabela
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = sqlite3.connect(self.db_path, timeout=10)
        cursor = conn.cursor()

        # Filtro
        filtro = self.filtro_status.get()
        mostrar_todos = self.mostrar_todos_var.get()
        hoje = date.today().isoformat()

        if filtro == 'Todos':
            if mostrar_todos:
                # Mostrar todos os pacientes
                cursor.execute("""
                    SELECT id, nome, telefone, data_consulta, hora_consulta,
                           status, tentativas_contato
                    FROM pacientes
                    ORDER BY data_consulta DESC, hora_consulta DESC
                """)
            else:
                # Mostrar apenas consultas futuras (hoje em diante)
                cursor.execute("""
                    SELECT id, nome, telefone, data_consulta, hora_consulta,
                           status, tentativas_contato
                    FROM pacientes
                    WHERE data_consulta >= ?
                    ORDER BY data_consulta, hora_consulta
                """, (hoje,))
        else:
            status_map = {
                'Pendente': 'pendente',
                'Mensagem Preparada': 'mensagem_preparada',
                'Enviada': 'mensagem_enviada',
                'Confirmado': 'confirmado',
                'Sem Resposta': 'sem_resposta',
                'Reagendado': 'reagendado'
            }

            status_filtro = status_map[filtro]

            if mostrar_todos:
                cursor.execute("""
                    SELECT id, nome, telefone, data_consulta, hora_consulta,
                           status, tentativas_contato
                    FROM pacientes
                    WHERE status = ?
                    ORDER BY data_consulta DESC, hora_consulta DESC
                """, (status_filtro,))
            else:
                cursor.execute("""
                    SELECT id, nome, telefone, data_consulta, hora_consulta,
                           status, tentativas_contato
                    FROM pacientes
                    WHERE status = ? AND data_consulta >= ?
                    ORDER BY data_consulta, hora_consulta
                """, (status_filtro, hoje))

        pacientes = cursor.fetchall()
        conn.close()
        
        # Inserir dados
        for paciente in pacientes:
            pid, nome, tel, data, hora, status, tentativas = paciente
            
            # Traduzir status
            status_display = {
                'pendente': 'Pendente',
                'mensagem_preparada': 'Mensagem Preparada',
                'mensagem_enviada': 'Enviada',
                'confirmado': 'Confirmado',
                'reagendado': 'Reagendado',
                'sem_resposta': 'Sem Resposta',
                'cancelado': 'Cancelado'
            }.get(status, status)
            
            # Colorir por status
            tag = ''
            if status == 'confirmado':
                tag = 'confirmado'
            elif status == 'sem_resposta':
                tag = 'sem_resposta'
            
            hora_formatada = str(hora)[:5] if hora else ''
            self.tree.insert(
                '',
                tk.END,
                values=(nome, tel, data, hora_formatada, status_display, tentativas),
                tags=(tag, str(pid))
            )
        
        # Configurar tags
        self.tree.tag_configure('confirmado', background='#d4edda')
        self.tree.tag_configure('sem_resposta', background='#f8d7da')
    
    def _on_double_click(self, event):
        """Duplo clique abre preparação de mensagem"""
        self._preparar_mensagem_selecionado()
    
    def _show_context_menu(self, event):
        """Mostra menu de contexto"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def _get_selected_id(self):
        """Retorna ID do paciente selecionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Atenção", "Selecione um paciente")
            return None
        
        item = selection[0]
        tags = self.tree.item(item, 'tags')
        
        # Último tag é o ID
        for tag in tags:
            if tag.isdigit():
                return int(tag)
        
        return None
    
    def _preparar_mensagem_selecionado(self):
        """Prepara mensagem para paciente selecionado"""
        paciente_id = self._get_selected_id()
        if paciente_id:
            self.on_preparar_mensagem(paciente_id)
    
    def _marcar_confirmado(self):
        """Marca paciente como confirmado"""
        paciente_id = self._get_selected_id()
        if not paciente_id:
            return
        
        if messagebox.askyesno("Confirmar", "Marcar como confirmado?"):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            from datetime import datetime
            
            cursor.execute("""
                UPDATE pacientes
                SET status = 'confirmado',
                    data_resposta = ?
                WHERE id = ?
            """, (datetime.now(), paciente_id))
            
            conn.commit()
            conn.close()
            
            self.atualizar_lista()
            messagebox.showinfo("Sucesso", "Paciente confirmado!")
    
    def _marcar_sem_resposta(self):
        """Marca paciente como sem resposta"""
        paciente_id = self._get_selected_id()
        if not paciente_id:
            return
        
        if messagebox.askyesno("Confirmar", "Marcar como sem resposta?"):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE pacientes
                SET status = 'sem_resposta'
                WHERE id = ?
            """, (paciente_id,))
            
            conn.commit()
            conn.close()
            
            self.atualizar_lista()

    def _alterar_status(self):
        """Abre diálogo para alterar status do paciente"""
        paciente_id = self._get_selected_id()
        if not paciente_id:
            return

        # Buscar status atual
        conn = sqlite3.connect(self.db_path, timeout=10)
        cursor = conn.cursor()

        cursor.execute("SELECT nome, status FROM pacientes WHERE id = ?", (paciente_id,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            return

        nome, status_atual = result

        # Opções de status
        status_options = {
            'pendente': 'Pendente',
            'mensagem_preparada': 'Mensagem Preparada',
            'mensagem_enviada': 'Mensagem Enviada',
            'confirmado': 'Confirmado',
            'reagendado': 'Reagendado',
            'sem_resposta': 'Sem Resposta',
            'cancelado': 'Cancelado'
        }

        # Criar diálogo simples
        dialog = tk.Toplevel(self.frame.winfo_toplevel())
        dialog.title(f"Alterar Status - {nome}")
        dialog.geometry("300x200")
        dialog.resizable(False, False)
        dialog.grab_set()

        ttk.Label(dialog, text="Novo Status:").pack(pady=10)

        status_var = tk.StringVar(value=status_options.get(status_atual, 'Pendente'))
        combo = ttk.Combobox(
            dialog,
            textvariable=status_var,
            values=list(status_options.values()),
            state='readonly'
        )
        combo.pack(pady=5)

        def salvar():
            novo_status_display = status_var.get()
            novo_status = [k for k, v in status_options.items() if v == novo_status_display][0]

            if messagebox.askyesno("Confirmar", f"Alterar status para '{novo_status_display}'?"):
                conn = sqlite3.connect(self.db_path, timeout=10)
                cursor = conn.cursor()

                cursor.execute("""
                    UPDATE pacientes
                    SET status = ?
                    WHERE id = ?
                """, (novo_status, paciente_id))

                conn.commit()
                conn.close()

                self.atualizar_lista()
                dialog.destroy()

        ttk.Button(dialog, text="Salvar", command=salvar).pack(pady=10)
        ttk.Button(dialog, text="Cancelar", command=dialog.destroy).pack()

    def _reagendar(self):
        """Abre diálogo para reagendar consulta"""
        paciente_id = self._get_selected_id()
        if not paciente_id:
            return

        from frontend.dialogs import RescheduleDialog
        RescheduleDialog(
            self.frame.winfo_toplevel(),
            self.db_path,
            paciente_id,
            on_rescheduled=self.atualizar_lista
        )

    def _reverter_reagendamento(self):
        """Reverte reagendamento, marcando paciente como pendente novamente"""
        paciente_id = self._get_selected_id()
        if not paciente_id:
            return

        if messagebox.askyesno("Reverter Reagendamento",
                              "Deseja reverter o reagendamento e marcar o paciente como pendente novamente?"):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE pacientes
                SET status = 'pendente'
                WHERE id = ?
            """, (paciente_id,))

            conn.commit()
            conn.close()

            self.atualizar_lista()
            messagebox.showinfo("Sucesso", "Reagendamento revertido. Paciente marcado como pendente.")
    
    def _excluir_paciente(self):
        """Exclui paciente (com confirmação)"""
        paciente_id = self._get_selected_id()
        if not paciente_id:
            return
        
        if messagebox.askyesno(
            "Confirmar Exclusão",
            "⚠️ Tem certeza que deseja excluir este paciente?\n\n"
            "Esta ação não pode ser desfeita!"
        ):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM pacientes WHERE id = ?", (paciente_id,))
            
            conn.commit()
            conn.close()
            
            self.atualizar_lista()
            messagebox.showinfo("Sucesso", "Paciente excluído")
    
    def _novo_paciente(self):
        """Abre diálogo para cadastrar novo paciente"""
        from frontend.dialogs import PatientDialog
        PatientDialog(
            self.frame.winfo_toplevel(),
            self.db_path,
            self.user_session,
            on_save_callback=self.atualizar_lista
        )

    def _importar_planilha(self):
        """Abre diálogo para importar planilha de pacientes"""
        from frontend.dialogs import ImportDialog
        ImportDialog(
            self.frame.winfo_toplevel(),
            self.db_path,
            self.user_session,
            on_import_callback=self.atualizar_lista
        )
    
    def _abrir_whatsapp(self):
        """Abre WhatsApp Web"""
        import webbrowser

        try:
            webbrowser.open("https://web.whatsapp.com")
            messagebox.showinfo("Sucesso", "WhatsApp Web aberto! Faça o login com QR Code.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir WhatsApp: {str(e)}")