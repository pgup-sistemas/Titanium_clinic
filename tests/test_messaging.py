import unittest
from backend.messaging import MessageManager

class TestMessaging(unittest.TestCase):
    def setUp(self):
        self.msg_manager = MessageManager(':memory:')
    
    def test_gerar_mensagem(self):
        # Teste básico de geração de mensagem
        pass

if __name__ == '__main__':
    unittest.main()