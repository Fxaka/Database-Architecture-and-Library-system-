import unittest
from unittest.mock import MagicMock, patch
from SERVICES.material_service import MaterialService
from CRUD.constants import MaterialStatus


class TestMaterialService(unittest.TestCase):
    def setUp(self):
        self.mock_conn = MagicMock()
        self.service = MaterialService(self.mock_conn)
        self.mock_crud = MagicMock()
        self.service.crud = self.mock_crud

    def test_add_material_validation(self):
        """测试资料添加验证"""
        # 测试空名称
        success, msg = self.service.add_new_material("", "作者", "出版社", 1)
        self.assertFalse(success)
        self.assertIn("不能为空", msg)

    def test_get_material_details(self):
        """测试获取资料详情"""
        test_material = {
            'material_id': 1,
            'status': MaterialStatus.AVAILABLE.value
        }
        self.mock_crud.get_material.return_value = test_material

        material = self.service.get_material_details(1)

        self.assertEqual(material['status_text'], 'AVAILABLE')
        self.mock_crud.get_material.assert_called_once_with(1)

    def test_update_material_status_invalid(self):
        """测试更新无效资料状态"""
        success, msg = self.service.update_material_status(1, 99)
        self.assertFalse(success)
        self.assertIn("无效状态值", msg)


if __name__ == '__main__':
    unittest.main()