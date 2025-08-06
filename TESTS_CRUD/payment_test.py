import unittest
from unittest.mock import MagicMock
from CRUD.payments_crud import PaymentCRUD


class TestPaymentCRUD(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.crud = PaymentCRUD(self.mock_db)
        self.mock_cursor = MagicMock()
        self.mock_db.cursor.return_value.__enter__.return_value = self.mock_cursor

    def test_record_payment_success(self):
        self.mock_cursor.fetchone.side_effect = [(1,), (101,)]

        success, payment_id = self.crud.record(1, 100.0)

        self.assertTrue(success)
        self.assertEqual(payment_id, 101)
        self.assertEqual(self.mock_cursor.execute.call_count, 3)


if __name__ == '__main__':
    unittest.main()