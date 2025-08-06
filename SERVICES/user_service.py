from typing import Tuple, Dict, Optional, Union
from DATABASE.transaction import transaction
from CRUD.users_crud import UserCRUD
from CRUD.loans_crud import LoanCRUD


class UserService:
    def __init__(self, db_connection):
        self.conn = db_connection
        self.user_crud = UserCRUD(db_connection)
        self.loan_crud = LoanCRUD(db_connection)

    def register_user(self, name: str, contact: str, user_type_id: int) -> Tuple[bool, Union[int, str]]:
        """Register a new user"""
        if not all([name.strip(), contact.strip()]):
            return False, "The name and contact information cannot be empty"
        return self.user_crud.create_user(name, contact, user_type_id)

    def get_user_with_borrowing_info(self, user_id: int) -> Optional[Dict]:
        """Get user details and borrowing information"""
        user = self.user_crud.get_user(user_id)
        if not user:
            return None

        # Get active loan records
        active_loans = self.loan_crud.get_active_loans_by_user(user_id)
        user.update({
            'active_loans': active_loans,
            'current_borrowings': len(active_loans),
            'max_borrowings': user.get('max_borrowings'),  # 添加最大借阅数量
            'max_borrowing_days': user.get('max_borrowing_days')  # 添加最大借阅天数
        })
        return user

    def delete_user(self, user_id: int) -> Tuple[bool, str]:
        """Delete a user (including transaction processing)"""
        try:
            with transaction(self.conn):
                # Check if there are any unreturned borrowings
                if self.loan_crud.get_active_loans_by_user(user_id):
                    return False, "The user has unreturned borrowing records"

                return self.user_crud.delete_user(user_id)
        except Exception as e:
            return False, f"Failed to delete the user: {str(e)}"

    def update_user_contact(self, user_id: int, new_contact: str) -> Tuple[bool, str]:
        """Update the user's contact information"""
        if not new_contact.strip():
            return False, "The contact information cannot be empty"
        return self.user_crud.update_user(user_id, contact=new_contact)