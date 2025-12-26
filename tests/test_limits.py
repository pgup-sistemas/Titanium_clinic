import unittest
from backend.limits import LimitsController

class TestLimits(unittest.TestCase):
    def setUp(self):
        self.limits = LimitsController(':memory:')
    
    def test_verificar_limite_diario(self):
        # Teste de limites diários
        pass

if __name__ == '__main__':
    unittest.main()