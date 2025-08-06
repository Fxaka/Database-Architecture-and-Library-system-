from datetime import datetime
from typing import Tuple, Union, List, Dict
from DATABASE.transaction import transaction


class PaymentCRUD:
    def __init__(self, db_connection):
        self.conn = db_connection

    def record(
            self,
            invoice_id: int,
            amount: float,
            method: str = 'cash'
    ) -> Tuple[bool, Union[int, str]]:
        sql_insert_payment = """
               INSERT INTO payments(invoice_id, amount, payment_date, method)
               VALUES (%s, %s, %s, %s)
               RETURNING payment_id
           """
        sql_update_invoice = "UPDATE invoices SET status = 2 WHERE invoice_id = %s"

        try:
            with transaction(self.conn):
                # Verify if the invoice exists
                with self.conn.cursor() as cursor:
                    cursor.execute("SELECT 1 FROM invoices WHERE invoice_id = %s", (invoice_id,))
                    invoice_exists = cursor.fetchone()
                    print(f"Invoice verification result: {bool(invoice_exists)}, Invoice ID: {invoice_id}")  # Add log output
                    if not invoice_exists:
                        return (False, "Invoice does not exist")

                    # Insert the payment record
                    cursor.execute(sql_insert_payment, (invoice_id, amount, datetime.now(), method))
                    payment_id = cursor.fetchone()[0]

                    # Update the invoice status to paid
                    cursor.execute(sql_update_invoice, (invoice_id,))

                return (True, payment_id)
        except Exception as e:
            print(f"Exception during payment record: {str(e)}")  # Add log output
            # The transaction will be rolled back automatically
            return (False, f"Payment recording failed: {str(e)}")

    def get_by_invoice(self, invoice_id: int) -> List[Dict]:
        """Get all payments for an invoice
        Args:
            invoice_id: ID of the invoice

        Returns:
            List of payment records
        """
        sql = """SELECT * FROM payments 
                 WHERE invoice_id=%s 
                 ORDER BY payment_date DESC"""
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (invoice_id,))
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_total_paid(self, invoice_id: int) -> float:
        """Get total amount paid towards an invoice
        Args:
            invoice_id: ID of the invoice

        Returns:
            Sum of all payments for this invoice
        """
        sql = "SELECT COALESCE(SUM(amount), 0) FROM payments WHERE invoice_id=%s"
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (invoice_id,))
            return float(cursor.fetchone()[0])