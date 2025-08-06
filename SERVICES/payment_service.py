import datetime as dt_class
from typing import Tuple, List, Dict, Optional
from CRUD.constants import InvoiceStatus
from CRUD.invoices_crud import InvoiceCRUD
from CRUD.payments_crud import PaymentCRUD
from CRUD.loans_crud import LoanCRUD
from CRUD.materials_crud import MaterialCRUD
from DATABASE.transaction import transaction
from CRUD.constants import MaterialStatus


class PaymentService:
    def __init__(self, db_connection):
        self.conn = db_connection
        self.payment_crud = PaymentCRUD(db_connection)
        self.invoice_crud = InvoiceCRUD(db_connection)
        self.loan_crud = LoanCRUD(db_connection)
        self.material_crud = MaterialCRUD(db_connection)

    def record_payment(self, invoice_id: int, amount: float, method: str = "cash") -> Tuple[bool, str]:
        """Record a payment (including the complete transaction)"""
        try:
            with transaction(self.conn):
                # Add detailed debugging information
                print(f"Starting to record the payment, Invoice ID: {invoice_id}, Amount: {amount}, Method: {method}")

                # 1. Verify the invoice
                invoice = self.invoice_crud.get_invoice(invoice_id)
                if not invoice:
                    print(f"Invoice does not exist: {invoice_id}")
                    return False, f"Invoice does not exist, ID: {invoice_id}"

                if invoice['status'] == InvoiceStatus.PAID.value:
                    print(f"Invoice has been paid: {invoice_id}")
                    return False, f"Invoice has been paid, ID: {invoice_id}"

                # 2. Record the payment
                print("Creating the payment record...")
                result = self.payment_crud.record(invoice_id, amount, method)
                if not result[0]:
                    print(f"Payment record failed: {result[1]}")
                    return result

                # 3. Double-confirm the payment status
                print("Verifying the payment status...")
                total_paid = self.payment_crud.get_total_paid(invoice_id)
                if total_paid < amount:
                    raise Exception(f"Insufficient payment amount, should pay: {amount}, already paid: {total_paid}")

                print("Payment process completed")
                return True, f"Payment successful, Payment ID: {result[1]}"

        except Exception as e:
            print(f"Payment transaction failed: {str(e)}")
            return False, f"Payment failed: {str(e)}"

    def pay_overdue_fee(self, loan_id: int) -> Tuple[bool, str]:
        try:
            with transaction(self.conn):
                # 1. Get the loan record
                loan = self.loan_crud._get_loan_info(loan_id)
                if not loan:
                    return False, "Loan record does not exist"

                # Query the user_id
                with self.conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT user_id FROM loans WHERE loan_id = %s
                    """, (loan_id,))
                    user_id_result = cursor.fetchone()
                    if not user_id_result:
                        return False, f"Unable to get the user ID, Loan record ID: {loan_id}"
                    user_id = user_id_result[0]

                # 2. Calculate the overdue fee
                success, late_fee, message = self.calculate_overdue_fee(loan_id)
                if not success or late_fee <= 0:
                    return False, "No overdue fee needs to be paid"

                # 3. Generate the invoice
                invoice_success, invoice_id = self.invoice_crud.create(
                    user_id=user_id,
                    amount=late_fee,
                    reason=f"Overdue return of material: {loan.get('material_name', '')}"
                )
                if not invoice_success:
                    return False, "Failed to generate the invoice"

                # 4. Confirm the invoice exists
                invoice = self.invoice_crud.get_invoice(invoice_id)
                if not invoice:
                    return False, "The invoice cannot be queried after generation"

                # 5. Record the payment
                payment_success, payment_message = self.record_payment(invoice_id, late_fee, "overdue")
                if not payment_success:
                    return False, payment_message

                # 6. Update the loan status
                self.loan_crud.update_loan(loan_id, {
                    'actual_return_date': dt_class.datetime.now(),
                    'late_fee': late_fee
                })

                # 7. Update the material status
                self.material_crud.update_material(loan['material_id'], {
                   'status': MaterialStatus.AVAILABLE.value
                })

                return True, "Payment successful"
        except Exception as e:
            return False, f"Payment failed: {str(e)}"

    def calculate_overdue_fee(self, loan_id: int) -> Tuple[bool, float, str]:
        """Calculate the overdue fee"""
        try:
            # Get the loan record and user type
            loan_info = self.loan_crud._get_loan_info(loan_id)
            print(f"Loan info: {loan_info}")  # Add log output
            if not loan_info:
                return False, 0.0, "Loan record does not exist"

            # Get the overdue rate rules
            rules = self.loan_crud._get_borrowing_rules(loan_info['user_type_id'])
            print(f"Borrowing rules: {rules}")  # Add log output
            if not rules:
                return False, 0.0, "Unable to get the overdue rate rules"

            # Assume the overdue rate is the third element of the tuple
            late_fee_per_day = float(rules[2])  # Modify here
            return_date = dt_class.datetime.now()

            # Date conversion processing
            due_date = loan_info['return_date']
            print(f"Due date: {due_date}, type: {type(due_date)}")  # Add log output
            if not isinstance(due_date, dt_class.datetime):
                if isinstance(due_date, dt_class.date):
                    due_date = dt_class.datetime.combine(due_date, dt_class.datetime.min.time())
                else:
                    due_date = dt_class.datetime.strptime(str(due_date), "%Y-%m-%d %H:%M:%S")

            # Calculate the number of overdue days
            days_overdue = max(0, (return_date - due_date).days)
            late_fee = round(days_overdue * late_fee_per_day, 2)

            return True, late_fee, "Overdue fee calculated successfully"
        except Exception as e:
            print(f"Exception: {str(e)}")  # Add log output
            return False, 0.0, f"Failed to calculate the overdue fee: {str(e)}"