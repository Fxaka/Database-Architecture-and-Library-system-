import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from CRUD.loans_crud import LoanCRUD


class TestLoanCRUD(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.crud = LoanCRUD(self.mock_db)
        self.mock_cursor = MagicMock()
        self.mock_db.cursor.return_value.__enter__.return_value = self.mock_cursor

    def test_create_loan_with_rules(self):
        """测试带规则的借阅创建"""
        # 模拟数据库返回规则
        self.mock_cursor.fetchone.side_effect = [
            (5, 56, 0.50),  # 规则查询
            (3,),  # 当前借阅量
            (101,)  # 新建借阅ID
        ]

        success, loan_id = self.crud.create_loan(1, 1, 1)
        self.assertTrue(success)
        self.assertEqual(loan_id, 101)

    def test_return_material_with_dynamic_fee(self):
        """测试动态逾期费计算"""
        test_data = [
            # (用户类型, 模拟费率, 逾期天数, 预期费用)
            (1, 0.50, 5, 2.50),  # student
            (2, 0.50, 3, 1.5),  # teacher
            (3, 0.70, 10, 7.00)  # staff
        ]

        for user_type, fee_rate, overdue_days, expected_fee in test_data:
            with self.subTest(user_type=user_type):
                # 模拟数据库返回
                self.mock_cursor.fetchone.side_effect = [
                    (1, datetime.now() - timedelta(days=overdue_days), user_type),
                    (None, None, fee_rate)  # 规则查询
                ]

                success, fee, _ = self.crud.return_material(1)
                self.assertTrue(success)
                self.assertAlmostEqual(fee, expected_fee, places=2)


if __name__ == '__main__':
    unittest.main()