import unittest
from unittest.mock import MagicMock
from SERVICES.loan_service import LoanService
from CRUD.constants import MaterialStatus

class TestLoanService(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.loan_service = LoanService(self.mock_db)
        self.loan_service.user_crud.get_user = MagicMock()
        self.loan_service.material_crud.get_material = MagicMock()
        self.loan_service.loan_crud.get_active_loans_by_user = MagicMock()
        self.loan_service.loan_crud.create_loan = MagicMock()

    def test_borrow_material_success(self):
        self.loan_service.user_crud.get_user.return_value = {'user_id': 1, 'user_type_id': 1, 'max_borrowings': 5}
        self.loan_service.material_crud.get_material.return_value = {'material_id': 1, 'status': MaterialStatus.AVAILABLE.value}
        self.loan_service.loan_crud.get_active_loans_by_user.return_value = []
        self.loan_service.loan_crud.create_loan.return_value = (True, 1001)

        success, message = self.loan_service.borrow_material(1, 1)
        self.assertTrue(success)
        self.assertEqual(message, "借阅成功，借阅ID: 1001")

    def test_borrow_material_fail_max_borrowings(self):
        self.loan_service.user_crud.get_user.return_value = {'user_id': 1, 'user_type_id': 1, 'max_borrowings': 2}
        self.loan_service.material_crud.get_material.return_value = {'material_id': 1, 'status': MaterialStatus.AVAILABLE.value}
        self.loan_service.loan_crud.get_active_loans_by_user.return_value = [{}, {}]  # 用户已借2本书

        success, message = self.loan_service.borrow_material(1, 1)
        self.assertFalse(success)
        self.assertEqual(message, "已达到最大借阅限制(2本)")

    def test_borrow_material_fail_unavailable(self):
        self.loan_service.user_crud.get_user.return_value = {'user_id': 1, 'user_type_id': 1, 'max_borrowings': 5}
        self.loan_service.material_crud.get_material.return_value = {'material_id': 1, 'status': MaterialStatus.BORROWED.value}

        success, message = self.loan_service.borrow_material(1, 1)
        self.assertFalse(success)
        self.assertEqual(message, "资料当前不可借阅")

if __name__ == "__main__":
    unittest.main()
