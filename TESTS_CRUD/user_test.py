import unittest
from unittest.mock import MagicMock
from CRUD.users_crud import UserCRUD


class TestUserCRUD(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.crud = UserCRUD(self.mock_db)

        # 创建完整的mock cursor链
        self.mock_cursor = MagicMock()
        self.mock_db.cursor.return_value.__enter__.return_value = self.mock_cursor

    def test_get_user_with_type_info(self):
        # 准备模拟数据 - 确保字段顺序与SQL查询一致
        mock_user_data = (
            101,  # user_id
            "林娟",  # name
            "lin@test.com",  # contact
            1,  # user_type_id
            "Student",  # type_name
            5,  # max_borrowings
            30  # max_borrowing_days
        )

        # 正确配置fetchone返回值
        self.mock_cursor.fetchone.return_value = mock_user_data

        # 配置cursor.description以支持字典转换
        self.mock_cursor.description = [
            ('user_id',), ('name',), ('contact',),
            ('user_type_id',), ('type_name',),
            ('max_borrowings',), ('max_borrowing_days',)
        ]

        # 执行测试
        user = self.crud.get_user(101)

        # 验证结果
        self.assertEqual(user["user_id"], 101)
        self.assertEqual(user["name"], "林娟")
        self.assertEqual(user["type_name"], "Student")

    def test_create_user_success(self):
        # 配置fetchone返回创建的user_id
        self.mock_cursor.fetchone.return_value = (101,)

        success, user_id = self.crud.create_user("吴辉", "wu@test.com", 1)

        self.assertTrue(success)
        self.assertEqual(user_id, 101)
        self.mock_db.commit.assert_called_once()


if __name__ == '__main__':
    unittest.main()