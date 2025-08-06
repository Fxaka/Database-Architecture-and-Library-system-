from datetime import datetime as dt_class
from typing import Tuple, List, Dict, Optional
from DATABASE.transaction import transaction
from CRUD.loans_crud import LoanCRUD
from CRUD.invoices_crud import InvoiceCRUD
from CRUD.materials_crud import MaterialCRUD
from CRUD.users_crud import UserCRUD
from CRUD.constants import MaterialStatus


class LoanService:
    def __init__(self, db_connection):
        self.conn = db_connection
        self.loan_crud = LoanCRUD(db_connection)
        self.invoice_crud = InvoiceCRUD(db_connection)
        self.material_crud = MaterialCRUD(db_connection)
        self.user_crud = UserCRUD(db_connection)

    def borrow_material(self, user_id: int, material_id: int) -> Tuple[bool, str]:
        """Borrow a material (including the complete transaction)"""
        try:
            with transaction(self.conn):
                user = self.user_crud.get_user(user_id)
                if not user:
                    return False, "The user does not exist"

                material = self.material_crud.get_material(material_id)
                if not material or material['status'] != MaterialStatus.AVAILABLE.value:
                    return False, "The material cannot be borrowed currently"

                active_loans = self.loan_crud.get_active_loans_by_user(user_id)
                if len(active_loans) >= user['max_borrowings']:
                    return False, f"Has reached the maximum borrowing limit ({user['max_borrowings']} books)"

                success, loan_id = self.loan_crud.create_loan(user_id, material_id, user['user_type_id'])
                if not success:
                    return False, "Borrowing failed"

                return True, f"Borrowing successful, Loan ID: {loan_id}"
        except Exception as e:
            return False, f"Borrowing failed: {str(e)}"

    def return_material(self, loan_id: int) -> Tuple[bool, str]:
        """Return a material (including the complete transaction)"""
        try:
            with transaction(self.conn):
                success, late_fee, message = self.loan_crud.return_material(loan_id)
                if not success:
                    return False, message

                if late_fee > 0:
                    loan_info = self._get_loan_info(loan_id)
                    if loan_info:
                        invoice_success, invoice_id = self.invoice_crud.create(
                            user_id=loan_info['user_id'],
                            amount=late_fee,
                            reason=f"Overdue return of material: {loan_info.get('material_name', '')}"
                        )
                        if not invoice_success:
                            raise Exception("Failed to generate the invoice")
                        message += f", Overdue fee generated: ¥{late_fee:.2f}"

                return True, message
        except Exception as e:
            return False, f"Return failed: {str(e)}"

    def get_overdue_loans_by_user(self, user_id: int) -> List[Dict]:
        """Get the overdue loan records of a specified user (improved version)"""
        sql = """
            SELECT 
                l.loan_id, 
                l.material_id, 
                m.material_name, 
                u.name as user_name,
                l.return_date,
                (CURRENT_DATE - l.return_date) AS overdue_days,
                m.status as material_status   --  Directly get the status from the query
            FROM loans l
            JOIN materials m ON l.material_id = m.material_id
            JOIN users u ON l.user_id = u.user_id
            WHERE l.user_id = %s
              AND l.actual_return_date IS NULL
              AND l.return_date < CURRENT_DATE
            ORDER BY l.return_date
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, (user_id,))
                columns = [desc[0] for desc in cursor.description]
                results = [dict(zip(columns, row)) for row in cursor.fetchall()]
                print(f"Debug information: Found {len(results)} overdue records")  # For debugging
                return results
        except Exception as e:
            print(f"Error querying overdue records: {str(e)}")
            return []

    def get_overdue_loans(self) -> List[Dict]:
        """Get all overdue loans"""
        return self.loan_crud.get_overdue_loans()

    def _get_loan_info(self, loan_id: int) -> Optional[Dict]:
        """Get loan details"""
        return self.loan_crud._get_loan_info(loan_id)

    def return_loan(self, loan_id: int) -> Tuple[bool, float, str]:
        """Return a loan and calculate late fee if applicable"""
        try:
            # 1. Get loan details
            loan = self.loan_crud._get_loan_info(loan_id)
            if not loan:
                return False, 0, "Loan not found"

            # 2. Calculate late fee
            # Assume that return_date here is the due date for return
            due_date = loan['return_date']
            if not isinstance(due_date, dt_class.date):
                if isinstance(due_date, dt_class.datetime):
                    due_date = due_date.date()
                else:
                    due_date = dt_class.datetime.strptime(str(due_date), "%Y-%m-%d").date()

            return_date = dt_class.datetime.now().date()
            late_days = max(0, (return_date - due_date).days)
            late_fee = late_days * 0.50  # $1 per day late fee

            # 3. Update loan record
            success, message = self.loan_crud.update_loan(loan_id, {
                'actual_return_date': return_date,  # Modify to the actual return date
                'late_fee': late_fee
            })
            if not success:
                return False, 0, message

            # 4. Update material status
            success, message = self.loan_crud.update_material_status(loan['material_id'],
                                                                     MaterialStatus.AVAILABLE.value)
            if not success:
                return False, 0, message

            return True, late_fee, "Material returned successfully"
        except Exception as e:
            return False, 0, str(e)

    def get_borrowing_rules(self, user_type_id: int) -> Optional[Dict]:
        return self.loan_crud._get_borrowing_rules(user_type_id)