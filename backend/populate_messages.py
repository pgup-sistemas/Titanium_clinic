import sqlite3
import random

def popular_mensagens(db_path: str):
    """
    Popula banco com 500+ variações de mensagens humanizadas
    """
    
    # ===== COMPONENTES DAS MENSAGENS =====
    
    aberturas = [
        "Oi, tudo bem?",
        "Olá!",
        "Bom dia!",
        "Boa tarde!",
        "Oi 😊",
        "E aí!",
        "Opa!",
        "Olá, como vai?",
        "Oi!",
        "Tudo bem por aí?",
        "Oi, td bem?",
        "Oii",
        "Olá! Tudo certo?",
        "Bom dia! 😊",
        "Boa tarde! ☀️",
        "Oi, espero que esteja bem!",
        "Olá, tudo tranquilo?",
        "Oi oi",
        "E aí, tudo bem?",
        "Opa! Tudo certo?"
    ]
    
    contextos_clinica = [
        "Aqui é da clínica.",
        "Falo da clínica.",
        "Entrando em contato da clínica.",
        "Sou da clínica.",
        "É da clínica aqui.",
        "Falando da clínica.",
        "Clínica aqui.",
        "Da clínica mandando mensagem.",
        "Clínica entrando em contato.",
        "É da equipe da clínica.",
        "Mandando mensagem da clínica.",
        "Clínica falando aqui.",
        "Da clínica pra você."
    ]
    
    acao_confirmacao = [
        "Só confirmando sua consulta para {data} às {hora}.",
        "Confirmando seu atendimento em {data} às {hora}.",
        "Sua consulta está marcada para {data} às {hora}.",
        "Lembrando que sua consulta é {data} às {hora}.",
        "Você tem consulta marcada para {data} às {hora}.",
        "Consulta agendada: {data} às {hora}.",
        "Seu horário é {data} às {hora}.",
        "Marcado para {data} às {hora}.",
        "Agendamos você para {data} às {hora}.",
        "Registramos sua consulta em {data} às {hora}.",
        "Você está agendado para {data} às {hora}.",
        "Confirmo sua consulta {data} às {hora}.",
        "Sua agenda: {data} às {hora}.",
        "Horário reservado: {data} às {hora}."
    ]
    
    pedido_confirmacao = [
        "Tudo certo?",
        "Pode me confirmar, por favor?",
        "Consegue confirmar?",
        "Confirmado?",
        "Confirma pra mim?",
        "Está ok para você?",
        "Podemos contar com você?",
        "Vai dar certo?",
        "Está mantido?",
        "Confirma presença?",
        "Pode vir?",
        "Consegue comparecer?",
        "Beleza pra você?",
        "Está bom esse horário?",
        "Mantém a consulta?",
        "Vem confirmar, pode ser?"
    ]
    
    fechamentos = [
        "Fico no aguardo 😊",
        "Aguardo retorno!",
        "Me avisa qualquer coisa.",
        "Qualquer dúvida, só falar!",
        "Estamos aqui.",
        "Até lá!",
        "Nos vemos!",
        "Abraço!",
        "Obrigado!",
        "Até breve!",
        "Te aguardo aqui.",
        "Responde quando puder.",
        "Fico aguardando confirmação.",
        "",  # Sem fechamento
        "",
        ""
    ]
    
    # ===== GERAR COMBINAÇÕES =====
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    mensagens_geradas = set()
    
    # PRIMEIRO CONTATO (200 mensagens)
    while len([m for m in mensagens_geradas if 'primeiro_contato' in m]) < 200:
        msg = " ".join([
            random.choice(aberturas),
            random.choice(contextos_clinica),
            random.choice(acao_confirmacao),
            random.choice(pedido_confirmacao),
            random.choice(fechamentos)
        ]).strip()
        
        mensagens_geradas.add(('primeiro_contato', msg))
    
    # CONFIRMAÇÃO (150 mensagens)
    while len([m for m in mensagens_geradas if m[0] == 'confirmacao']) < 150:
        msg = " ".join([
            random.choice(aberturas),
            random.choice(acao_confirmacao),
            random.choice(pedido_confirmacao),
            random.choice(fechamentos)
        ]).strip()
        
        mensagens_geradas.add(('confirmacao', msg))
    
    # LEMBRETE (100 mensagens)
    lembretes = [
        "Lembrete: sua consulta é amanhã, {data} às {hora}.",
        "Oi! Amanhã você tem consulta às {hora}.",
        "Lembrando: amanhã {data} às {hora}.",
        "Não esqueça: amanhã às {hora}!",
        "Sua consulta é amanhã às {hora}. 😊",
        "Amanhã {data} às {hora}, combinado?",
        "Consulta amanhã: {hora}.",
        "Te aguardo amanhã às {hora}!"
    ]
    
    for _ in range(100):
        msg = " ".join([
            random.choice(aberturas),
            random.choice(lembretes),
            random.choice(fechamentos)
        ]).strip()
        mensagens_geradas.add(('lembrete', msg))
    
    # REAGENDAMENTO (50 mensagens)
    reagendar = [
        "Entendi que precisa reagendar. Qual data seria melhor para você?",
        "Sem problemas! Que dia funciona melhor?",
        "Tranquilo! Qual horário prefere?",
        "Podemos remarcar sim! Qual seria melhor?",
        "Claro! Me passa uma data que funcione pra você.",
        "Combinado! Qual dia você prefere?",
        "Ok! Temos outras opções de horário.",
        "Vamos remarcar então. Qual data é boa?"
    ]
    
    for _ in range(50):
        msg = " ".join([
            random.choice(aberturas),
            random.choice(reagendar)
        ]).strip()
        mensagens_geradas.add(('reagendamento', msg))
    
    # FOLLOW-UP (100 mensagens)
    followup = [
        "Oi! Vi que não consegui falar com você antes. Consegue confirmar a consulta de {data}?",
        "Oi novamente! Sobre a consulta de {data} às {hora}, consegue confirmar?",
        "Tentei falar antes, tudo ok para {data}?",
        "Oi! Sobre sua consulta de {data}, pode confirmar?",
        "Voltando ao assunto: {data} às {hora} está mantido?",
        "Oi! Conseguiu ver minha mensagem anterior? Consulta {data} confirmada?",
        "Retorno sobre a consulta: {data} às {hora} ok?",
        "Oi! Sobre a consulta de {data}, tudo certo?"
    ]
    
    for _ in range(100):
        msg = " ".join([
            random.choice(followup),
            random.choice(pedido_confirmacao),
            random.choice(fechamentos)
        ]).strip()
        mensagens_geradas.add(('follow_up', msg))
    
    # ===== INSERIR NO BANCO =====
    
    print(f"Gerando {len(mensagens_geradas)} mensagens unicas...")

    for tipo, texto in mensagens_geradas:
        cursor.execute("""
            INSERT OR IGNORE INTO mensagens (tipo, texto, ativo)
            VALUES (?, ?, 1)
        """, (tipo, texto))

    conn.commit()

    # Verificar quantas foram inseridas
    cursor.execute("SELECT COUNT(*) FROM mensagens")
    total = cursor.fetchone()[0]

    print(f"{total} mensagens no banco!")
    
    conn.close()

if __name__ == "__main__":
    popular_mensagens('data/titanium_clinica.db')