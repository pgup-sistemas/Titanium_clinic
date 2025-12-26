import webbrowser
import urllib.parse
import time

class WhatsAppAutomation:
    def __init__(self):
        pass

    def colar_mensagem(self, telefone: str, mensagem: str) -> bool:
        """
        Abre WhatsApp Web e cola mensagem (NÃO ENVIA)

        ⚠️ IMPORTANTE: Esta função APENAS abre o WhatsApp Web.
        O atendente DEVE colar a mensagem e pressionar ENTER manualmente.

        Args:
            telefone: Número no formato +5511999999999
            mensagem: Texto da mensagem

        Returns:
            bool: True se conseguiu abrir, False caso contrário
        """
        try:
            # Formatar número
            numero_limpo = telefone.replace('+', '').replace(' ', '')

            # Abrir chat direto via URL com mensagem
            url = f"https://web.whatsapp.com/send?phone={numero_limpo}&text={urllib.parse.quote(mensagem)}"

            # Abrir no navegador padrão
            webbrowser.open(url)

            # Pequena pausa para carregamento
            time.sleep(2)

            return True

        except Exception as e:
            print(f"Erro ao abrir WhatsApp: {str(e)}")
            return False

    def verificar_whatsapp_ativo(self, telefone: str) -> bool:
        """
        Verifica se número tem WhatsApp ativo

        NOTA: Esta versão simplificada sempre retorna True
        """
        return True  # Versão simplificada

    def fechar(self):
        """Não há navegador para fechar nesta versão"""
        pass

    def __del__(self):
        self.fechar()