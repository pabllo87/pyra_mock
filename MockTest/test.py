import unittest
# wymaga do zainstalowania z pip'a, require unittest
from mock import MagicMock, Mock, patch, call
from StringIO import StringIO

from . import main
from .models import Car


class ProductionClassTest(unittest.TestCase):

    def testAssertOnce(self):
        """
        asercja sprawsza czy metoda zostala wykonana tylko raz
        uwaga: nie bierze pod uwage parametrow
        """
        real = main.ProductionClass()
        real.something = MagicMock()
        real.method(1, 2, 3)
        real.something.assert_called_once_with(1, 2, 3)
        #real.method(1, 2, 4)
        #real.something.assert_called_once_with(1, 2, 4)

    def testAssertWithParams(self):
        """
        asercja sprawdza czy metoda zostala wywolana z podanymi parametrami
        uwaga: asercja dotyczy tylko ostatniego wywolania metody
        """
        real = main.ProductionClass()
        real.something = MagicMock()
        real.method(1, 2, 3)
        #real.method(1, 2, 4)
        real.something.assert_called_with(1, 2, 3)

    def testCheckcalledMethod(self):
        """
        metoda closer przyjmuje jako paremetr obkiet i wywoluje jego
        metode close, na koncu asercja sprawdza czy metoda close zostala
        wywolana. Nie musimy jawnie jej mockowac, obiekt Mock zalatwi to
        za nas
        """
        real = main.ProductionClass()
        mock = Mock()
        real.closer(mock)
        mock.close.assert_called_with()

    @patch('os.getpid', lambda: 666)
    def testMockReturnValue(self):
        """
        przekazanie funkcji lambda jako cialo metody
        przekazanie samej wartosci nie zadziala poniewaz getpaid jest
        metoda a nie polem i zostaje wywolana
        TypeError: 'int' object is not callable
        """
        real = main.ProductionClass()
        self.assertEqual(666, real.pid())

    def testMockDatetime(self):
        """
        datetime jest modulem napisanym w C, nie mozna w prosty
        sposob patchowac date.today
        """
        from datetime import date
        with patch('MockTest.main.date') as mock_date:
            mock_date.today.return_value = date(2010, 10, 8)
            mock_date.side_effect = lambda *args, **kw: date(*args, **kw)

            self.assertEqual(main.date.today(), date(2010, 10, 8))
            self.assertEqual(main.date(2009, 6, 8), date(2009, 6, 8))

    def testMockGenerator(self):
        real = main.ProductionClass()
        real.iter = MagicMock()
        real.iter.return_value = iter([1, 2, 3])

        self.assertEqual(list(real.iter()), [1, 2, 3])

    def testShowCalledArgs(self):
        """
        metoda call_args_list pokazuje nam liste parametrow z jakimi
        zostala wywoalna mockowana funkcja/metoda
        """
        real = main.ProductionClass()
        real.something = MagicMock()
        real.method(1, 2, 3)
        real.method(2, 2, 3)
        expected = [call(1, 2, 3), call(2, 2, 3)]
        self.assertEqual(real.something.call_args_list, expected)

    def testSideEffect(self):
        returns = ['BAD', 'OK']

        real = main.ProductionClass()
        real.empty = Mock(side_effect=returns)

        self.assertEqual(real.empty(), returns[0])
        self.assertEqual(real.empty(), returns[1])

    def testSideEffectException(self):
        class SideException(Exception):
            pass
        returns = [SideException(), 'OK']

        def side_effect(*args):
            result = returns.pop(0)
            if isinstance(result, Exception):
                raise result
            return result
        real = main.ProductionClass()
        real.empty = Mock(side_effect=side_effect)

        with self.assertRaises(SideException):
            real.empty()

        self.assertEqual(real.empty(), 'OK')

    def testCompareMockAndMagicMock(self):
        """
        Mock wywala sie bledem
        TypeError: 'Mock' object does not
        support item assignment
        """

        mock = MagicMock()
        #mock = Mock()
        mock[3] = 'fish'
        mock.__getitem__.return_value = 'result'
        self.assertEqual(mock[2], 'result')

    def testMagicMock(self):
        """
        Mock konczy sie z informacja, ze nie posiada
        atrybutu __eq__
        """
        mock = MagicMock()
        self.assertNotEqual(mock, 3)
        mock.__eq__.return_value = True
        self.assertEqual(mock, 3)

    def testCarSpec(self):
        """
        Mock udaje klase Car
        """
        mock_instance = Mock(spec=Car)
        mock_instance.marka = "Porsche"
        mock_instance.model = "911"
        self.assertEqual(Car.__unicode__(mock_instance), "Porsche 911")
        self.assertEqual(Car.get_model(mock_instance), "911")

    def testCarMock(self):
        """
        Mock django orm, method count
        """
        with patch('MockTest.models.Car.objects.count', return_value=1):
            self.assertEqual(Car.objects.count(), 1)

    def testMockFile(self):
        filename = MagicMock(spec=file, wraps=StringIO('test'))
        self.assertTrue(isinstance(filename, file))
        self.assertEqual(filename.read(), 'test')

    def testMockFileOpen(self):
        filename = MagicMock(spec=file, wraps=StringIO('test'))
        with patch('__builtin__.open', return_value=filename):
            filename = open('test.txt')
            self.assertTrue(isinstance(filename, file))
            self.assertEqual(filename.read(), 'test')

    def testMockRequest(self):
        with patch('requests.post', return_value=main.Response(200, 'TestMock')) as MockRequest:
            prod = main.ProductionClass()
            response = prod.request_test('google.pl', {'foo': 'bar'})
            instance = MockRequest.call_args
            data = instance[1]['data']
            self.assertEqual(instance[0], ('google.pl',))
            self.assertEqual(data['foo'], 'bar')
            self.assertEqual(response, 'TestMock')

    def testMockRequestException(self):

        with patch('requests.post', return_value=main.Response(404, 'TestMock')):
            prod = main.ProductionClass()
            with self.assertRaises(main.Exception404):
                prod.request_test('google.pl', {'foo': 'bar'})
