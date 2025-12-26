# Scripts Utilitários - Titanium Clínica

## generate_secret_key.py

Script para gerar uma SECRET_KEY segura para o sistema.

### Uso:

**Gerar chave (apenas mostrar):**
```bash
python scripts/generate_secret_key.py
```

**Gerar e adicionar ao .env automaticamente:**
```bash
python scripts/generate_secret_key.py --env
```

### O que faz:
- Gera uma chave secreta segura de 32 bytes usando `secrets.token_urlsafe()`
- Pode adicionar automaticamente ao arquivo `.env`
- Mostra instruções para uso manual se preferir

---

## setup_production.py

Script completo de configuração para produção.

### Uso:
```bash
python scripts/setup_production.py
```

### O que faz:
1. Verifica se arquivo `.env` existe
2. Gera SECRET_KEY se necessário
3. Atualiza/cria arquivo `.env` com SECRET_KEY
4. Verifica se `.env` está no `.gitignore`
5. Cria `.gitignore` com configurações adequadas se não existir

---

## Recomendações de Segurança

1. **NUNCA** faça commit do arquivo `.env` no Git
2. Use o script `generate_secret_key.py` para gerar chaves seguras
3. Mantenha o arquivo `.env` no `.gitignore`
4. Use uma SECRET_KEY diferente para cada ambiente (desenvolvimento, produção)

---

## Exemplo de Arquivo .env

```env
# Configurações do Titanium Clínica

# Database
DB_PATH=data/titanium_clinica.db

# Security
SECRET_KEY=sua-chave-secreta-gerada-aqui
```

