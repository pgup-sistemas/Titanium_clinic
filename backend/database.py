import sqlite3
from pathlib import Path

def criar_banco(db_path: str = 'data/titanium_clinica.db'):
    """Cria banco de dados com todas as tabelas"""
    
    # Criar diretório se não existir
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Schema completo
    schema_sql = """
-- ============================================
-- USUÁRIOS E AUTENTICAÇÃO
-- ============================================

CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL,
    nome_completo TEXT NOT NULL,
    email TEXT UNIQUE,
    perfil TEXT CHECK(perfil IN ('admin', 'gestor', 'atendente')) NOT NULL,
    ativo BOOLEAN DEFAULT 1,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    ultimo_acesso DATETIME,
    criado_por INTEGER,
    FOREIGN KEY (criado_por) REFERENCES usuarios(id)
);

CREATE TABLE sessoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    token TEXT UNIQUE NOT NULL,
    ip_maquina TEXT,
    data_login DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_logout DATETIME,
    ativo BOOLEAN DEFAULT 1,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

-- ============================================
-- PACIENTES E CONSENTIMENTO LGPD
-- ============================================

CREATE TABLE pacientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    telefone TEXT NOT NULL,
    telefone_formatado TEXT,
    email TEXT,
    data_nascimento DATE,
    cpf TEXT,
    
    -- Consulta
    data_consulta DATE NOT NULL,
    hora_consulta TIME NOT NULL,
    tipo_consulta TEXT,
    profissional TEXT,
    observacoes TEXT,
    
    -- Status da confirmação
    status TEXT CHECK(status IN (
        'pendente',
        'mensagem_preparada',
        'mensagem_enviada',
        'confirmado',
        'reagendado',
        'cancelado',
        'sem_resposta'
    )) DEFAULT 'pendente',
    
    -- Mensagem preparada
    mensagem_preparada TEXT,
    fase_conversa TEXT DEFAULT 'primeiro_contato',
    data_preparo DATETIME,
    data_envio DATETIME,
    data_resposta DATETIME,
    
    -- LGPD
    consentimento_whatsapp BOOLEAN DEFAULT 0,
    data_consentimento DATETIME,
    consentimento_obtido_por INTEGER,
    forma_consentimento TEXT CHECK(forma_consentimento IN ('verbal', 'escrito', 'digital')),
    termos_versao TEXT,
    
    -- Controle
    tentativas_contato INTEGER DEFAULT 0,
    ultima_tentativa DATETIME,
    numero_valido BOOLEAN DEFAULT 1,
    whatsapp_ativo BOOLEAN DEFAULT 1,
    
    -- Auditoria
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
    cadastrado_por INTEGER,
    data_atualizacao DATETIME,
    atualizado_por INTEGER,
    
    FOREIGN KEY (consentimento_obtido_por) REFERENCES usuarios(id),
    FOREIGN KEY (cadastrado_por) REFERENCES usuarios(id),
    FOREIGN KEY (atualizado_por) REFERENCES usuarios(id)
);

CREATE INDEX idx_pacientes_telefone ON pacientes(telefone);
CREATE INDEX idx_pacientes_data_consulta ON pacientes(data_consulta);
CREATE INDEX idx_pacientes_status ON pacientes(status);

-- ============================================
-- BANCO DE MENSAGENS (500+)
-- ============================================

CREATE TABLE mensagens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT CHECK(tipo IN (
        'primeiro_contato',
        'confirmacao',
        'lembrete',
        'reagendamento',
        'follow_up'
    )) NOT NULL,
    texto TEXT NOT NULL,
    categoria TEXT,
    tom TEXT CHECK(tom IN ('formal', 'amigavel', 'neutro')),
    usa_emoji BOOLEAN DEFAULT 0,
    variacao_grupo INTEGER,
    ativo BOOLEAN DEFAULT 1,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_mensagens_tipo ON mensagens(tipo);

-- ============================================
-- HISTÓRICO DE MENSAGENS
-- ============================================

CREATE TABLE historico_mensagens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id INTEGER NOT NULL,
    mensagem_id INTEGER,
    mensagem_texto TEXT NOT NULL,
    tipo_mensagem TEXT NOT NULL,
    data_preparacao DATETIME,
    data_envio DATETIME,
    enviado_por INTEGER,
    status_envio TEXT CHECK(status_envio IN (
        'preparada',
        'enviada',
        'respondida',
        'sem_resposta'
    )),
    FOREIGN KEY (paciente_id) REFERENCES pacientes(id),
    FOREIGN KEY (mensagem_id) REFERENCES mensagens(id),
    FOREIGN KEY (enviado_por) REFERENCES usuarios(id)
);

-- ============================================
-- CONTROLE DE LIMITES ANTI-BLOQUEIO
-- ============================================

CREATE TABLE controle_envio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data DATE NOT NULL,
    numero_telefone TEXT NOT NULL,
    tipo_mensagem TEXT NOT NULL,
    total_enviado INTEGER DEFAULT 0,
    ultimo_envio DATETIME,
    usuario_id INTEGER,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    UNIQUE(data, numero_telefone)
);

CREATE TABLE limites_sistema (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_limite TEXT UNIQUE NOT NULL,
    valor_limite INTEGER NOT NULL,
    descricao TEXT,
    ativo BOOLEAN DEFAULT 1
);

-- Inserir limites padrão
INSERT INTO limites_sistema (tipo_limite, valor_limite, descricao) VALUES
('max_primeiros_contatos_dia', 30, 'Máximo de primeiros contatos por dia'),
('intervalo_minimo_segundos', 120, 'Intervalo mínimo entre envios (2 min)'),
('max_tentativas_paciente', 3, 'Máximo de tentativas por paciente'),
('horario_inicio', 8, 'Horário início de envios (8h)'),
('horario_fim', 20, 'Horário fim de envios (20h)');

-- ============================================
-- LOG DE AUDITORIA
-- ============================================

CREATE TABLE log_auditoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    acao TEXT NOT NULL,
    tabela TEXT,
    registro_id INTEGER,
    dados_anteriores TEXT,
    dados_novos TEXT,
    ip_maquina TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

CREATE INDEX idx_audit_usuario ON log_auditoria(usuario_id);
CREATE INDEX idx_audit_timestamp ON log_auditoria(timestamp);

-- ============================================
-- CONFIGURAÇÕES DO SISTEMA
-- ============================================

CREATE TABLE configuracoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chave TEXT UNIQUE NOT NULL,
    valor TEXT,
    tipo TEXT CHECK(tipo IN ('string', 'integer', 'boolean', 'json')),
    descricao TEXT,
    editavel BOOLEAN DEFAULT 1,
    data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Configurações padrão
INSERT INTO configuracoes (chave, valor, tipo, descricao) VALUES
('nome_clinica', 'Clínica Exemplo', 'string', 'Nome da clínica'),
('telefone_clinica', '', 'string', 'Telefone da clínica'),
('backup_automatico', 'true', 'boolean', 'Ativar backup automático'),
('backup_hora', '23:00', 'string', 'Horário do backup automático'),
('dias_retencao_backup', '7', 'integer', 'Dias de retenção de backups');

-- ============================================
-- RELATÓRIOS E ESTATÍSTICAS
-- ============================================

CREATE TABLE relatorios_diarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data DATE UNIQUE NOT NULL,
    total_pacientes INTEGER DEFAULT 0,
    confirmados INTEGER DEFAULT 0,
    aguardando_resposta INTEGER DEFAULT 0,
    reagendados INTEGER DEFAULT 0,
    sem_resposta INTEGER DEFAULT 0,
    cancelados INTEGER DEFAULT 0,
    taxa_confirmacao REAL,
    gerado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TERMOS LGPD
-- ============================================

CREATE TABLE termos_lgpd (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    versao TEXT UNIQUE NOT NULL,
    texto_completo TEXT NOT NULL,
    data_vigencia DATE NOT NULL,
    ativo BOOLEAN DEFAULT 1,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Termo inicial
INSERT INTO termos_lgpd (versao, texto_completo, data_vigencia) VALUES
('1.0', 'Termo de Consentimento para Tratamento de Dados Pessoais...', date('now'));
"""
    
    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()
    
    print(f"Banco criado em: {db_path}")

def criar_usuario_admin(db_path: str, username: str, password: str):
    """Cria primeiro usuário admin"""
    from backend.auth import AuthManager
    
    auth = AuthManager(db_path)
    result = auth.criar_usuario(
        username=username,
        password=password,
        nome_completo="Administrador",
        email="admin@clinica.com",
        perfil="admin",
        criado_por=None
    )
    
    if result['success']:
        print(f"Usuario admin criado: {username}")
    else:
        print(f"Erro: {result['message']}")

if __name__ == "__main__":
    criar_banco()
    criar_usuario_admin('data/titanium_clinica.db', 'admin', 'admin123')