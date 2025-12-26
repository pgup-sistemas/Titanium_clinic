"""
Script de configuração para produção
Cria SECRET_KEY e configura ambiente
"""

import os
import sys
from pathlib import Path

def verificar_env_file():
    """Verifica se arquivo .env existe e tem SECRET_KEY"""
    env_path = Path('.env')
    
    if not env_path.exists():
        print("[!] Arquivo .env nao encontrado. Criando...")
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write("# Configuracoes do Titanium Clinica\n")
        return False
    
    # Verificar se SECRET_KEY existe
    with open(env_path, 'r', encoding='utf-8') as f:
        conteudo = f.read()
        if 'SECRET_KEY=' in conteudo:
            # Verificar se não é o valor padrão
            if 'change-me-in-production' in conteudo:
                print("[!] SECRET_KEY ainda esta com valor padrao!")
                return False
            return True
    
    return False

def main():
    print("\n" + "="*60)
    print("  Configuracao para Producao - Titanium Clinica")
    print("="*60 + "\n")
    
    # Verificar .env
    if verificar_env_file():
        print("[OK] Arquivo .env ja existe e tem SECRET_KEY configurada")
    else:
        print("[*] Gerando SECRET_KEY...")
        # Importar e executar gerador
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from scripts.generate_secret_key import gerar_secret_key, atualizar_env_file
        
        secret_key = gerar_secret_key()
        atualizar_env_file(secret_key)
        print("[OK] SECRET_KEY gerada e adicionada ao .env\n")
    
    # Verificar .gitignore
    gitignore_path = Path('.gitignore')
    if gitignore_path.exists():
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            if '.env' not in conteudo:
                print("[*] Adicionando .env ao .gitignore...")
                with open(gitignore_path, 'a', encoding='utf-8') as f:
                    f.write("\n# Arquivo de configuracao com credenciais\n.env\n")
                print("[OK] .env adicionado ao .gitignore")
            else:
                print("[OK] .env ja esta no .gitignore")
    else:
        print("[*] Criando .gitignore...")
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write("# Arquivo de configuracao com credenciais\n.env\n")
        print("[OK] .gitignore criado com .env")
    
    print("\n" + "="*60)
    print("  Configuracao concluida!")
    print("="*60)
    print("\n[!] IMPORTANTE:")
    print("  1. Revise o arquivo .env antes de fazer commit")
    print("  2. Certifique-se de que .env esta no .gitignore")
    print("  3. Nao compartilhe o arquivo .env publicamente\n")

if __name__ == "__main__":
    main()

