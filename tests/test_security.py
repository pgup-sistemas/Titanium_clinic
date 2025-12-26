import unittest
from backend.security import SecurityValidator

class TestSecurity(unittest.TestCase):
    def setUp(self):
        self.security = SecurityValidator(':memory:')
    
    def test_validar_telefone(self):
        # Teste de validação de telefone
        valido, numero, erro = self.security.validar_telefone('+5511999999999')
        self.assertTrue(valido)

if __name__ == '__main__':
    unittest.main()