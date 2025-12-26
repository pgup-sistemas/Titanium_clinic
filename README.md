# Titanium Clínica - Sistema de Confirmação Humanizada no WhatsApp

Sistema desktop seguro para clínicas que organiza contatos, prepara mensagens humanizadas e auxilia na confirmação de consultas via WhatsApp, com conformidade LGPD e proteção anti-bloqueio.

## 🚀 Características

- ✅ Desktop Windows/Linux com Python puro e Tkinter
- ✅ Banco SQLite criptografado
- ✅ Sistema de login e perfis (admin, gestor, atendente)
- ✅ Automação assistida (nunca envia sozinho)
- ✅ 500+ variações de mensagens humanizadas
- ✅ Dashboard com gráficos em tempo real
- ✅ Conformidade total com LGPD
- ✅ Backup automático e logs de auditoria
- ✅ Controle anti-bloqueio do WhatsApp

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Google Chrome (para automação WhatsApp)
- Conexão com internet

## 🛠️ Instalação

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/titanium-clinica.git
   cd titanium-clinica
   ```

2. **Crie ambiente virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   ```

3. **Instale dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Primeira execução:**
   ```bash
   python app.py
   ```

   Na primeira execução, o sistema irá:
   - Criar o banco de dados
   - Solicitar criação do usuário administrador
   - Popular o banco com 500+ mensagens

## 🎯 Como Usar

### 1. Login
- Use as credenciais criadas na primeira execução
- Perfis disponíveis: admin, gestor, atendente

### 2. Gerenciar Pacientes
- Visualize a lista de pacientes pendentes
- Clique duplo em um paciente para preparar mensagem
- Ou use o botão "Preparar Mensagem"

### 3. Preparar Mensagem
- Sistema gera mensagem humanizada automaticamente
- Revise o texto no preview
- Clique "Enviar via WhatsApp" para colar no navegador
- **IMPORTANTE:** Pressione ENTER manualmente para enviar

### 4. Dashboard
- Visualize estatísticas diárias
- Gráficos de confirmações e status
- Disponível apenas para admin/gestor

## 🔒 Segurança e LGPD

### Proteções Implementadas
- **Nunca envia automaticamente** - sempre requer confirmação manual
- **Limites anti-bloqueio** - máximo 30 contatos/dia, intervalos de 2 min
- **Consentimento LGPD** - obrigatório para envio
- **Logs de auditoria** - todas as ações são registradas
- **Backup automático** - dados protegidos contra perda

### Conformidade LGPD
- Coleta apenas dados necessários
- Consentimento explícito para WhatsApp
- Direito de exclusão e correção
- Transparência no tratamento

## 📊 Funcionalidades

### Para Atendentes
- Visualizar pacientes
- Preparar mensagens
- Marcar status de confirmação
- Enviar via WhatsApp

### Para Gestores
- Todas as funções de atendente
- Dashboard com estatísticas
- Relatórios
- Gerenciamento de usuários

### Para Administradores
- Todas as funções de gestor
- Configurações do sistema
- Backup e restauração
- Logs de auditoria

## 🏗️ Arquitetura

```
titanium_clinica/
├── app.py                 # Ponto de entrada
├── config.py              # Configurações
├── backend/               # Lógica de negócio
│   ├── auth.py           # Autenticação
│   ├── database.py       # Conexão BD
│   ├── messaging.py      # Geração de mensagens
│   ├── limits.py         # Controle anti-bloqueio
│   ├── security.py       # Validações LGPD
│   └── ...
├── frontend/              # Interface Tkinter
│   ├── login_window.py   # Tela de login
│   ├── main_window.py    # Janela principal
│   ├── patient_view.py   # Lista pacientes
│   └── ...
├── automation/            # WhatsApp Web
│   └── whatsapp.py       # Integração (apenas cola)
├── data/                  # Dados e backups
├── assets/                # Recursos visuais
├── docs/                  # Documentação
└── tests/                 # Testes unitários
```

## 📈 Roadmap

### v2.1 (Próximos 3 meses)
- Editor visual de mensagens
- Importação de planilhas Excel
- Relatórios em PDF
- Integração com calendários

### v2.2 (6 meses)
- Multi-clínica (franquias)
- API REST para integrações
- App mobile complementar
- IA para sugestão de horários

### v3.0 (1 ano)
- WhatsApp Business API oficial
- Chatbot para respostas automáticas
- Integração com sistemas de gestão
- Modo SaaS (nuvem)

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

## ⚠️ Avisos Importantes

- **Uso Responsável:** O sistema foi desenvolvido para uso ético e em conformidade com os termos do WhatsApp
- **LGPD:** Certifique-se de obter consentimento explícito dos pacientes
- **Backup:** Sempre faça backup dos dados importantes
- **Suporte:** Para suporte, consulte a documentação em `docs/`

## 📞 Suporte

- **Documentação:** `docs/manual_usuario.md`
- **Guia de Implementação:** `docs/guia_implementacao.md`
- **Política LGPD:** `docs/politica_lgpd.md`

---

**Titanium Clínica v2.0** - Sistema seguro e humanizado para confirmação de consultas.