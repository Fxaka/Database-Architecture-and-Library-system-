from datetime import datetime
from typing import Tuple, Union, List, Dict
from CRUD.constants import InvoiceStatus
from typing import Optional


class InvoiceCRUD:
    def __init__(self, db_connection):
        self.conn = db_connection

    def create(
            self,
            user_id: int,
            amount: float,
            reason: str
    ) -> Tuple[bool, Union[int, str]]:
        """Create a new invoice
        Args:
            user_id: ID of the user being invoiced
            amount: Invoice amount
            reason: Reason for invoice (e.g. "Late return")

        Returns:
            (success, invoice_id/error_message)
        """
        sql = """INSERT INTO invoices(user_id, amount, invoice_date, reason, status)
                 VALUES (%s, %s, %s, %s, %s) RETURNING invoice_id"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, (
                    user_id,
                    amount,
                    datetime.now(),
                    reason,
                    InvoiceStatus.UNPAID.value  # Default status
                ))
                inv_id = cursor.fetchone()[0]
                self.conn.commit()
                return (True, inv_id)
        except Exception as e:
            self.conn.rollback()
            return (False, str(e))

    def get_unpaid_by_user(self, user_id: int) -> List[Dict]:
        """Get all unpaid invoices for a user
        Args:
            user_id: ID of the user

        Returns:
            List of unpaid invoice records
        """
        sql = """SELECT i.* FROM invoices i
                 LEFT JOIN payments p ON i.invoice_id = p.invoice_id
                 WHERE i.user_id=%s AND p.payment_id IS NULL
                 AND i.status = %s
                 ORDER BY i.invoice_date DESC"""
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (user_id, InvoiceStatus.UNPAID.value))
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def mark_as_paid(self, invoice_id: int) -> Tuple[bool, str]:
        """Mark invoice as paid (without recording payment details)
        Args:
            invoice_id: ID of invoice to mark

        Returns:
            (success, message)
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE invoices SET status=%s WHERE invoice_id=%s",
                    (InvoiceStatus.PAID.value, invoice_id)
                )
                self.conn.commit()
                return (True, "Invoice marked as paid")
        except Exception as e:
            self.conn.rollback()
            return (False, str(e))

    def get_by_user(self, user_id):
        pass

    def get_invoice(self, invoice_id):
        pass

    def get_invoice(self, invoice_id: int) -> Optional[Dict]:
        """Get invoice by ID"""
        sql = "SELECT * FROM invoices WHERE invoice_id = %s"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, (invoice_id,))
                result = cursor.fetchone()
                if result:
                    columns = [desc[0] for desc in cursor.description]
                    invoice = dict(zip(columns, result))
                    print(f"Invoice query successful: {invoice}")
                    return invoice
                else:
                    print(f"Invoice does not exist: {invoice_id}")
                    return None
        except Exception as e:
            print(f"Error fetching invoice: {str(e)}")
            return None