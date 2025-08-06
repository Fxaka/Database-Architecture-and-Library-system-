import unittest
from unittest.mock import MagicMock, patch
from SERVICES.reservation_service import ReservationService
from CRUD.constants import MaterialStatus


class TestReservationService(unittest.TestCase):
    def setUp(self):
        self.mock_conn = MagicMock()
        self.service = ReservationService(self.mock_conn)

        # 配置模拟CRUD
        self.mock_reservation_crud = MagicMock()
        self.mock_material_crud = MagicMock()
        self.mock_user_crud = MagicMock()

        self.service.reservation_crud = self.mock_reservation_crud
        self.service.material_crud = self.mock_material_crud
        self.service.user_crud = self.mock_user_crud

    def test_make_reservation_success(self):
        """测试成功预约资料"""
        # 配置模拟数据
        self.mock_user_crud.get_user.return_value = {'user_id': 1}
        self.mock_material_crud.get_material.return_value = {
            'material_id': 1,
            'status': MaterialStatus.AVAILABLE.value
        }
        self.mock_reservation_crud.create.return_value = (True, 3001)

        # 执行测试
        success, result = self.service.make_reservation(1, 1)

        # 验证结果
        self.assertTrue(success)
        self.assertIn("3001", result)
        self.mock_reservation_crud.create.assert_called_once_with(1, 1)

    def test_cancel_reservation(self):
        """测试取消预约"""
        self.mock_reservation_crud.cancel.return_value = (True, "取消成功")

        success, msg = self.service.cancel_reservation(1)

        self.assertTrue(success)
        self.assertEqual(msg, "取消成功")


if __name__ == '__main__':
    unittest.main()