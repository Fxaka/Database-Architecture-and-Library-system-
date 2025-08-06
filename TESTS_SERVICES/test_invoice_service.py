import unittest
from unittest.mock import MagicMock
from SERVICES.invoice_service import InvoiceService


class TestInvoiceService(unittest.TestCase):
    def setUp(self):
        self.mock_conn = MagicMock()
        self.service = InvoiceService(self.mock_conn)

        # 配置模拟CRUD
        self.mock_invoice_crud = MagicMock()
        self.mock_payment_crud = MagicMock()
        self.mock_loan_crud = MagicMock()

        self.service.invoice_crud = self.mock_invoice_crud
        self.service.payment_crud = self.mock_payment_crud
        self.service.loan_crud = self.mock_loan_crud

    def test_generate_late_fee_invoice(self):
        """测试生成逾期发票"""
        # 模拟逾期借阅记录
        self.mock_loan_crud.get_overdue_loans_by_user.return_value = [
            {'loan_id': 1, 'late_fee': 10.5}
        ]
        self.mock_invoice_crud.create.return_value = (True, 4001)

        success, invoice_id = self.service.generate_late_fee_invoice(1)

        self.assertTrue(success)
        self.assertEqual(invoice_id, 4001)
        self.mock_invoice_crud.create.assert_called_once_with(1, 10.5, "逾期借阅罚款")

    def test_get_user_invoices(self):
        """测试获取用户发票列表"""
        test_invoices = [{'invoice_id': 1, 'amount': 10.0}]
        self.mock_invoice_crud.get_unpaid_by_user.return_value = test_invoices
        self.mock_payment_crud.get_by_invoice.return_value = [
            {'amount': 5.0}, {'amount': 3.0}
        ]

        invoices = self.service.get_user_invoices(1)

        self.assertEqual(len(invoices), 1)
        self.assertEqual(invoices[0]['outstanding_amount'], 2.0)


if __name__ == '__main__':
    unittest.main()