import unittest
from unittest.mock import MagicMock, patch
from SERVICES.user_service import UserService


class TestUserService(unittest.TestCase):
    def setUp(self):
        """初始化测试环境"""
        self.mock_conn = MagicMock()
        self.service = UserService(self.mock_conn)

        # 配置模拟CRUD
        self.mock_user_crud = MagicMock()
        self.mock_loan_crud = MagicMock()
        self.service.user_crud = self.mock_user_crud
        self.service.loan_crud = self.mock_loan_crud

    def test_register_user_success(self):
        """测试用户注册成功"""
        self.mock_user_crud.create_user.return_value = (True, 123)

        success, user_id = self.service.register_user("张三", "13800138000", 1)

        self.assertTrue(success)
        self.assertEqual(user_id, 123)
        self.mock_user_crud.create_user.assert_called_once_with("张三", "13800138000", 1)

    def test_register_user_validation_fail(self):
        """测试用户注册验证失败"""
        # 测试空姓名
        success, msg = self.service.register_user("", "13800138000", 1)
        self.assertFalse(success)
        self.assertIn("不能为空", msg)

        # 测试空联系方式
        success, msg = self.service.register_user("张三", "", 1)
        self.assertFalse(success)
        self.assertIn("不能为空", msg)

    def test_delete_user_with_active_loans(self):
        """测试删除有未归还借阅的用户"""
        self.mock_loan_crud.get_active_loans_by_user.return_value = [{"loan_id": 1}]

        success, msg = self.service.delete_user(1)

        self.assertFalse(success)
        self.assertIn("未归还", msg)
        self.mock_loan_crud.get_active_loans_by_user.assert_called_once_with(1)


if __name__ == '__main__':
    unittest.main()