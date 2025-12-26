"""
Script para gerar SECRET_KEY seguro para o sistema Titanium Clínica

Uso:
    python scripts/generate_secret_key.py
    
Ou para adicionar diretamente ao .env:
    python scripts/generate_secret_key.py --env
"""

import secrets
import os
import sys
from pathlib import Path

def gerar_secret_key():
    """Gera uma chave secreta segura de 32 bytes"""
    return secrets.token_urlsafe(32)

def atualizar_env_file(secret_key: str):
    """Atualiza ou cria arquivo .env com SECRET_KEY"""
    env_path = Path('.env')
    
    linhas = []
    secret_key_existe = False
    
    # Ler arquivo existente se houver
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for linha in f:
                if linha.strip().startswith('SECRET_KEY='):
                    linhas.append(f'SECRET_KEY={secret_key}\n')
                    secret_key_existe = True
                else:
                    linhas.append(linha)
    
    # Adicionar SECRET_KEY se não existir
    if not secret_key_existe:
        linhas.append(f'SECRET_KEY={secret_key}\n')
    
    # Escrever arquivo
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(linhas)
    
    print(f"[OK] SECRET_KEY adicionada ao arquivo .env")
    print(f"     Arquivo: {env_path.absolute()}")

def main():
    secret_key = gerar_secret_key()
    
    print("\n" + "="*60)
    print("  Gerador de SECRET_KEY - Titanium Clinica")
    print("="*60 + "\n")
    
    print(f"SECRET_KEY gerada:")
    print(f"  {secret_key}\n")
    
    # Verificar se deve atualizar .env
    if '--env' in sys.argv or '-e' in sys.argv:
        atualizar_env_file(secret_key)
        print(f"\n[!] IMPORTANTE: Adicione o arquivo .env ao .gitignore se ainda nao estiver!")
    else:
        print("Para adicionar automaticamente ao arquivo .env, execute:")
        print("  python scripts/generate_secret_key.py --env\n")
        print("Ou adicione manualmente ao arquivo .env:")
        print(f"  SECRET_KEY={secret_key}\n")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

