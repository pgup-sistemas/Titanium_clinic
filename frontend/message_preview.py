import tkinter as tk
from tkinter import ttk, messagebox
from backend.messaging import MessageManager
from backend.limits import LimitsController
from backend.security import SecurityValidator
from automation.whatsapp import WhatsAppAutomation
import sqlite3

class MessagePreview:
    def __init__(self, parent, db_path: str, paciente_id: int, user_session: dict, on_enviado):
        self.db_path = db_path
        self.paciente_id = paciente_id
        self.user_session = user_session
        self.on_enviado = on_enviado
        
        self.msg_manager = MessageManager(db_path)
        self.limits = LimitsController(db_path)
        self.security = SecurityValidator(db_path)
        self.whatsapp = WhatsAppAutomation()
        
        # Janela modal
        self.window = tk.Toplevel(parent)
        self.window.title("Preparar Mensagem")
        self.window.geometry("600x500")
        self.window.resizable(False, False)
        self.window.grab_set()  # Modal
        
        self._carregar_dados_paciente()
        self._criar_interface()
        self._centralizar()
    
    def _carregar_dados_paciente(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT nome, telefone, data_consulta, hora_consulta,
                   tipo_consulta, status, mensagem_preparada,
                   consentimento_whatsapp
            FROM pacientes
            WHERE id = ?
        """, (self.paciente_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            messagebox.showerror("Erro", "Paciente não encontrado")
            self.window.destroy()
            return
        
        self.paciente = {
            'nome': result[0],
            'telefone': result[1],
            'data_consulta': result[2],
            'hora_consulta': result[3],
            'tipo_consulta': result[4],
            'status': result[5],
            'mensagem_preparada': result[6],
            'consentimento': result[7]
        }
    
    def _criar_interface(self):
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Dados do Paciente
        info_frame = ttk.LabelFrame(main_frame, text="Dados do Paciente", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(info_frame, text=f"Nome: {self.paciente['nome']}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Telefone: {self.paciente['telefone']}").pack(anchor=tk.W)
        hora_formatada = str(self.paciente['hora_consulta'])[:5] if self.paciente['hora_consulta'] else ''
        ttk.Label(info_frame, text=f"Data: {self.paciente['data_consulta']} às {hora_formatada}").pack(anchor=tk.W)
        
        # Verificar consentimento
        if not self.paciente['consentimento']:
            ttk.Label(
                info_frame,
                text="⚠️  ATENÇÃO: Paciente sem consentimento LGPD",
                foreground="red"
            ).pack(anchor=tk.W, pady=5)
        
        # Mensagem
        msg_frame = ttk.LabelFrame(main_frame, text="Mensagem", padding="10")
        msg_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.text_mensagem = tk.Text(msg_frame, height=10, wrap=tk.WORD)
        self.text_mensagem.pack(fill=tk.BOTH, expand=True)
        
        # Se já tem mensagem preparada, exibir
        if self.paciente['mensagem_preparada']:
            self.text_mensagem.insert(1.0, self.paciente['mensagem_preparada'])
            self.text_mensagem.config(state=tk.DISABLED)
        
        # Botões - usar atributo para poder atualizar depois
        self.btn_frame = ttk.Frame(main_frame)
        self.btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        self._atualizar_botoes()
    
    def _preparar_mensagem(self):
        # Verificar consentimento
        if not self.paciente['consentimento']:
            if not messagebox.askyesno(
                "Consentimento LGPD",
                "Paciente não possui consentimento registrado.\n\n"
                "Você obteve consentimento verbal/escrito do paciente "
                "para envio de mensagens via WhatsApp?"
            ):
                return
            
            # Registrar consentimento
            self._registrar_consentimento_manual()
        
        # Verificar limites
        pode_enviar, msg_limite = self.limits.verificar_limite_diario()
        if not pode_enviar:
            messagebox.showwarning("Limite Atingido", msg_limite)
            return
        
        pode_enviar, msg_numero = self.limits.verificar_limite_por_numero(self.paciente['telefone'])
        if not pode_enviar:
            messagebox.showwarning("Limite Atingido", msg_numero)
            return
        
        # Verificar horário
        pode_enviar, msg_horario = self.security.verificar_horario_permitido()
        if not pode_enviar:
            messagebox.showwarning("Horário Inválido", msg_horario)
            return
        
        # Determinar tipo de mensagem baseado no status
        tipo_msg = self._determinar_tipo_mensagem()
        
        # Gerar mensagem
        result = self.msg_manager.preparar_mensagem_paciente(self.paciente_id, tipo_msg)
        
        if result['success']:
            # Atualizar campo de texto (permitir edição para revisão)
            self.text_mensagem.config(state=tk.NORMAL)
            self.text_mensagem.delete(1.0, tk.END)
            self.text_mensagem.insert(1.0, result['mensagem'])
            # Manter editável para permitir ajustes antes de enviar
            
            # Recarregar dados do paciente para atualizar status
            self._carregar_dados_paciente()
            
            # Atualizar botões - mostrar opções de envio
            self._atualizar_botoes_pos_preparacao()
            
            messagebox.showinfo(
                "Sucesso",
                "Mensagem preparada com sucesso!\n\n"
                "Revise o texto e clique em 'Enviar via WhatsApp' "
                "para colar no WhatsApp Web."
            )
            
            # Atualizar lista principal se callback disponível
            if self.on_enviado:
                self.on_enviado()
        else:
            messagebox.showerror("Erro", result['message'])
    
    def _enviar_whatsapp(self):
        mensagem = self.text_mensagem.get(1.0, tk.END).strip()
        
        if not mensagem:
            messagebox.showwarning("Atenção", "Mensagem vazia")
            return
        
        # Confirmar ação
        if not messagebox.askyesno(
            "Confirmar Envio",
            f"A mensagem será colada no WhatsApp Web.\n\n"
            f"Você precisará:\n"
            f"1. Revisar o texto\n"
            f"2. Pressionar ENTER manualmente\n\n"
            f"Deseja continuar?"
        ):
            return
        
        try:
            # Abrir WhatsApp e colar mensagem
            sucesso = self.whatsapp.colar_mensagem(
                self.paciente['telefone'],
                mensagem
            )
            
            if sucesso:
                # Atualizar status para "mensagem_enviada"
                self._atualizar_status_enviado()
                
                # Registrar no controle de limites
                self.limits.registrar_envio(
                    self.paciente['telefone'],
                    self._determinar_tipo_mensagem(),
                    self.user_session['user_id']
                )
                
                messagebox.showinfo(
                    "Sucesso",
                    "Mensagem colada no WhatsApp Web!\n\n"
                    "⚠️ IMPORTANTE: Revise o texto e pressione ENTER para enviar."
                )
                
                self.window.destroy()
                if self.on_enviado:
                    self.on_enviado()
            else:
                messagebox.showerror(
                    "Erro",
                    "Não foi possível abrir o WhatsApp Web.\n\n"
                    "Verifique se está logado no navegador."
                )
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar: {str(e)}")
    
    def _determinar_tipo_mensagem(self) -> str:
        """Determina tipo de mensagem baseado no status atual"""
        status = self.paciente['status']
        
        if status == 'pendente':
            return 'primeiro_contato'
        elif status in ['mensagem_preparada', 'mensagem_enviada']:
            return 'confirmacao'
        elif status == 'sem_resposta':
            return 'follow_up'
        
        return 'confirmacao'
    
    def _atualizar_botoes(self):
        """Atualiza botões baseado no estado atual"""
        # Limpar botões existentes
        for widget in self.btn_frame.winfo_children():
            widget.destroy()
        
        if self.paciente.get('mensagem_preparada'):
            # Mensagem já preparada - mostrar botão de enviar
            ttk.Button(
                self.btn_frame,
                text="📱 Enviar via WhatsApp",
                command=self._enviar_whatsapp
            ).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(
                self.btn_frame,
                text="🔄 Gerar Nova Mensagem",
                command=self._gerar_nova_mensagem
            ).pack(side=tk.LEFT, padx=5)
        else:
            # Preparar nova mensagem
            ttk.Button(
                self.btn_frame,
                text="✨ Preparar Mensagem",
                command=self._preparar_mensagem
            ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            self.btn_frame,
            text="Cancelar",
            command=self.window.destroy
        ).pack(side=tk.RIGHT, padx=5)
    
    def _atualizar_botoes_pos_preparacao(self):
        """Atualiza botões após preparar mensagem"""
        self._atualizar_botoes()
    
    def _gerar_nova_mensagem(self):
        """Permite gerar uma nova variação da mensagem"""
        self.text_mensagem.config(state=tk.NORMAL)
        self._preparar_mensagem()
    
    def _registrar_consentimento_manual(self):
        """Registra consentimento obtido manualmente"""
        from backend.lgpd import LGPDManager
        
        lgpd = LGPDManager(self.db_path)
        lgpd.registrar_consentimento(
            self.paciente_id,
            'verbal',
            self.user_session['user_id'],
            'Consentimento obtido durante preparação de mensagem'
        )
    
    def _atualizar_status_enviado(self):
        """Atualiza status do paciente após envio"""
        conn = sqlite3.connect(self.db_path, timeout=10)
        cursor = conn.cursor()
        
        from datetime import datetime
        
        try:
            agora = datetime.now()
            
            # Buscar data_preparo para incluir no histórico
            cursor.execute("""
                SELECT data_preparo FROM pacientes WHERE id = ?
            """, (self.paciente_id,))
            result_prep = cursor.fetchone()
            data_preparacao = result_prep[0] if result_prep and result_prep[0] else agora
            
            # Atualizar status do paciente
            cursor.execute("""
                UPDATE pacientes
                SET status = 'mensagem_enviada',
                    data_envio = ?,
                    tentativas_contato = tentativas_contato + 1,
                    ultima_tentativa = ?
                WHERE id = ?
            """, (agora, agora, self.paciente_id))
            
            # Registrar no histórico com data_preparacao
            cursor.execute("""
                INSERT INTO historico_mensagens 
                (paciente_id, mensagem_texto, tipo_mensagem, data_preparacao,
                 data_envio, enviado_por, status_envio)
                VALUES (?, ?, ?, ?, ?, ?, 'enviada')
            """, (
                self.paciente_id,
                self.text_mensagem.get(1.0, tk.END).strip(),
                self._determinar_tipo_mensagem(),
                data_preparacao,
                agora,
                self.user_session['user_id']
            ))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _centralizar(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')