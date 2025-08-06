import unittest
from unittest.mock import MagicMock
from CRUD.materials_crud import MaterialCRUD
from CRUD.constants import MaterialStatus


class TestMaterialCRUD(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.crud = MaterialCRUD(self.mock_db)
        self.mock_cursor = MagicMock()
        self.mock_db.cursor.return_value.__enter__.return_value = self.mock_cursor

    def test_create_material_success(self):
        self.mock_cursor.fetchone.return_value = (101,)

        success, mat_id = self.crud.create_material("Book", "Author", "Pub", 1)

        self.assertTrue(success)
        self.assertEqual(mat_id, 101)

    def test_get_available_materials(self):
        mock_data = [(101, "Book1"), (102, "Book2")]
        self.mock_cursor.fetchall.return_value = mock_data
        self.mock_cursor.description = [('id',), ('name',)]

        materials = self.crud.get_available_materials()

        self.assertEqual(len(materials), 2)


if __name__ == '__main__':
    unittest.main()