from datetime import datetime as dt_class, date, timedelta
from typing import Tuple, Union, List, Dict, Optional
from DATABASE.transaction import transaction
from CRUD.constants import MaterialStatus, UserType
from datetime import datetime, timedelta, date


class LoanCRUD:
    def __init__(self, db_connection):
        self.conn = db_connection

    def _get_borrowing_rules(self, user_type_id: int) -> Optional[dict]:
        """Read borrowing rules from the database"""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                SELECT max_borrowings, max_borrowing_days, 0.5 as late_fee_per_day 
                FROM user_types 
                WHERE type_id = %s
            """, (user_type_id,))
            return cursor.fetchone()

    def create_loan(self, user_id: int, material_id: int, user_type_id: int) -> Tuple[bool, Union[int, str]]:
        """Create a borrowing record (dynamic rules version)"""
        try:
            rules = self._get_borrowing_rules(user_type_id)
            if not rules:
                return False, "Invalid user type or no rule configured"

            max_books, max_days, _ = rules

            with transaction(self.conn):
                with self.conn.cursor() as cursor:
                    # Check the borrowing quantity limit
                    cursor.execute("""
                        SELECT COUNT(*) FROM loans 
                        WHERE user_id = %s AND actual_return_date IS NULL
                    """, (user_id,))
                    if cursor.fetchone()[0] >= max_books:
                        return False, f"The maximum borrowing limit has been reached({max_books} books)"

                    # Create a borrowing record
                    cursor.execute("""
                        INSERT INTO loans(user_id, material_id, loan_date, return_date)
                        VALUES (%s, %s, CURRENT_DATE, CURRENT_DATE + %s)
                        RETURNING loan_id
                    """, (user_id, material_id, timedelta(days=max_days)))
                    loan_id = cursor.fetchone()[0]

                    # Update the material status
                    cursor.execute("""
                        UPDATE materials 
                        SET status = %s 
                        WHERE material_id = %s
                    """, (MaterialStatus.BORROWED.value, material_id))

                    return (True, loan_id)
        except Exception as e:
            return (False, f"Failed to borrow: {str(e)}")

    def return_material(self, loan_id: int) -> Tuple[bool, float, str]:
        """Return of information (dynamic acquisition of overdue rates)"""
        # Get the borrowing record and user type
        with self.conn.cursor() as cursor:
            cursor.execute("""
                SELECT l.material_id, l.return_date, u.user_type_id
                FROM loans l
                JOIN users u ON l.user_id = u.user_id
                WHERE l.loan_id = %s AND l.actual_return_date IS NULL
            """, (loan_id,))
            record = cursor.fetchone()

        if not record:
            return (False, 0.0, "No valid borrowing records found")

        material_id, due_date, user_type_id = record

        # Get the overdue rate rules
        rules = self._get_borrowing_rules(user_type_id)
        if not rules:
            return (False, 0.0, "Unable to get overdue rate rules")

        _, _, late_fee_per_day = rules
        return_date = dt_class.now()

        # Date conversion processing
        if not isinstance(due_date, dt_class):
            if isinstance(due_date, date):
                due_date = dt_class.combine(due_date, dt_class.min.time())
            else:
                due_date = dt_class.strptime(str(due_date), "%Y-%m-%d %H:%M:%S")

        # Calculate the number of overdue days
        due_date = due_date.replace(tzinfo=None)
        return_date = return_date.replace(tzinfo=None)
        days_overdue = 0

        if return_date > due_date:
            delta = return_date - due_date
            days_overdue = delta.days
            if delta.seconds > 43200:  # 12 hours
                days_overdue += 1

        late_fee = round(days_overdue * late_fee_per_day, 2)

        # Update the database
        try:
            with transaction(self.conn):
                with self.conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE loans 
                        SET actual_return_date = %s 
                        WHERE loan_id = %s
                    """, (return_date, loan_id))

                    cursor.execute("""
                        UPDATE materials 
                        SET status = %s 
                        WHERE material_id = %s
                    """, (MaterialStatus.AVAILABLE.value, material_id))

            return (True, late_fee, "The return process was successful")
        except Exception as e:
            return (False, 0.0, f"Return processing failed: {str(e)}")

    def get_overdue_loans(self) -> List[Dict[str, Union[int, str, date]]]:
        """Get all overdue borrowing records"""
        sql = """
            SELECT l.*, u.name, m.material_name
            FROM loans l
            JOIN users u ON l.user_id = u.user_id
            JOIN materials m ON l.material_id = m.material_id
            WHERE l.actual_return_date IS NULL 
              AND l.return_date < CURRENT_DATE
            ORDER BY l.return_date
        """
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            return self._dict_results(cursor)

    def _dict_results(self, cursor) -> List[Dict[str, Union[int, str, date]]]:
        """Convert query results to a list of dictionaries"""
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_reservations_by_user(self, user_id: int) -> List[Dict]:
        """Get the user's reservation records"""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                SELECT r.reservation_id, m.material_name, r.reservation_date 
                FROM reservations r
                JOIN materials m ON r.material_id = m.material_id
                WHERE r.user_id = %s
            """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_active_loans_by_user(self, user_id):
        """Get the user's current unreturned borrowing records"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM loans 
                    WHERE user_id = %s 
                    AND actual_return_date IS NULL
                """, (user_id,))
                return self._dict_results(cursor)  # Use the existing _dict_results method
        except Exception as e:
            print(f"Error getting active loans: {str(e)}")
            return []

    def get_active_loan_by_user_and_material(self, user_id, material_id):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM loans
                    WHERE user_id = %s AND material_id = %s AND return_date IS NULL
                """, (user_id, material_id))
                return cursor.fetchone()
        except Exception as e:
            self.conn.rollback()
            return None

    def _get_loan_info(self, loan_id):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT l.material_id, l.return_date, u.user_type_id
                    FROM loans l
                    JOIN users u ON l.user_id = u.user_id
                    WHERE l.loan_id = %s AND l.actual_return_date IS NULL
                """, (loan_id,))
                record = cursor.fetchone()
                if record:
                    columns = ['material_id', 'return_date', 'user_type_id']
                    return dict(zip(columns, record))
                return None
        except Exception as e:
            print(f"Failed to get borrowing record: {str(e)}")
            return None

    def update_loan(self, loan_id: int, update_data: Dict) -> Tuple[bool, str]:
        """Update the borrowing record"""
        try:
            with transaction(self.conn):
                cursor = self.conn.cursor()
                # Remove the late_fee field
                if 'late_fee' in update_data:
                    del update_data['late_fee']

                update_fields = ", ".join([f"{key} = %s" for key in update_data.keys()])
                update_values = list(update_data.values()) + [loan_id]
                sql = f"UPDATE loans SET {update_fields} WHERE loan_id = %s"
                cursor.execute(sql, update_values)
                self.conn.commit()
                return True, "Borrowing record updated successfully"
        except Exception as e:
            self.conn.rollback()
            return False, f"Failed to update borrowing record: {str(e)}"

