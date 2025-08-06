
import unittest
from CRUD.constants import MaterialStatus, LoanStatus, InvoiceStatus

class TestConstants(unittest.TestCase):
    def test_material_status_values(self):
        self.assertEqual(MaterialStatus.AVAILABLE, 1)
        self.assertEqual(MaterialStatus.BORROWED, 2)
        self.assertEqual(MaterialStatus.RESERVED, 3)

    def test_loan_status_values(self):
        self.assertEqual(LoanStatus.ACTIVE, 1)
        self.assertEqual(LoanStatus.RETURNED, 2)
        self.assertEqual(LoanStatus.OVERDUE, 3)

    def test_invoice_status_values(self):
        self.assertEqual(InvoiceStatus.UNPAID, 1)
        self.assertEqual(InvoiceStatus.PAID, 2)

if __name__ == '__main__':
    unittest.main()