import unittest
from unittest.mock import MagicMock
from CRUD.reservations_crud import ReservationCRUD


class TestReservationCRUD(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.crud = ReservationCRUD(self.mock_db)
        self.mock_cursor = MagicMock()
        self.mock_db.cursor.return_value.__enter__.return_value = self.mock_cursor

    def test_create_reservation_success(self):
        self.mock_cursor.fetchone.side_effect = [(1,), (101,)]

        success, res_id = self.crud.create(1, 1)

        self.assertTrue(success)
        self.assertEqual(res_id, 101)


if __name__ == '__main__':
    unittest.main()