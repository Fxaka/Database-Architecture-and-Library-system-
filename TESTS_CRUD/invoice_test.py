import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from CRUD.invoices_crud import InvoiceCRUD
from CRUD.constants import InvoiceStatus


class TestInvoiceCRUD(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.crud = InvoiceCRUD(self.mock_db)
        self.mock_cursor = MagicMock()
        self.mock_db.cursor.return_value.__enter__.return_value = self.mock_cursor

    def test_create_invoice_success(self):
        self.mock_cursor.fetchone.return_value = (101,)

        success, inv_id = self.crud.create(1, 100.0, "Late fee")

        self.assertTrue(success)
        self.assertEqual(inv_id, 101)
        self.mock_db.commit.assert_called_once()

    def test_create_invoice_failure(self):
        self.mock_cursor.execute.side_effect = Exception("DB error")

        success, message = self.crud.create(1, 100.0, "Late fee")

        self.assertFalse(success)
        self.assertIn("DB error", message)
        self.mock_db.rollback.assert_called_once()

    def test_get_unpaid_by_user(self):
        mock_data = [(1, 100.0, "Late fee")]
        self.mock_cursor.fetchall.return_value = mock_data
        self.mock_cursor.description = [('id',), ('amount',), ('reason',)]

        invoices = self.crud.get_unpaid_by_user(1)

        self.assertEqual(len(invoices), 1)
        self.assertEqual(invoices[0]['amount'], 100.0)


if __name__ == '__main__':
    unittest.main()