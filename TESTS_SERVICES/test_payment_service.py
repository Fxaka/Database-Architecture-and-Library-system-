import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# 将项目根目录添加到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from SERVICES.payment_service import PaymentService
from CRUD.constants import InvoiceStatus


class TestPaymentService(unittest.TestCase):
    def setUp(self):
        self.mock_conn = MagicMock()
        self.service = PaymentService(self.mock_conn)

        # 配置模拟CRUD
        self.mock_payment_crud = MagicMock()
        self.mock_invoice_crud = MagicMock()

        self.service.payment_crud = self.mock_payment_crud
        self.service.invoice_crud = self.mock_invoice_crud

    @patch('SERVICES.payment_service.transaction')
    def test_record_payment_success(self, mock_transaction):
        """测试记录支付成功"""
        # 配置模拟数据
        self.mock_invoice_crud.get_invoice.return_value = {
            'invoice_id': 1,
            'amount': 10.0,
            'status': InvoiceStatus.UNPAID.value
        }
        self.mock_payment_crud.record.return_value = (True, 5001)
        self.mock_payment_crud.get_total_paid.return_value = 10.0

        # 执行测试
        success, result = self.service.record_payment(1, 10.0)

        # 验证结果
        self.assertTrue(success)
        self.assertIn("5001", result)
        self.mock_invoice_crud.mark_as_paid.assert_called_once_with(1)

    def test_get_invoice_payments(self):
        """测试获取发票支付记录"""
        test_payments = [{'payment_id': 1, 'amount': 5.0}]
        self.mock_payment_crud.get_by_invoice.return_value = test_payments

        payments = self.service.get_invoice_payments(1)

        self.assertEqual(len(payments), 1)
        self.assertEqual(payments[0]['amount'], 5.0)


if __name__ == '__main__':
    unittest.main()
