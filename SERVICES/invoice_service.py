from typing import List, Dict, Tuple, Union
from DATABASE.transaction import transaction
from CRUD.invoices_crud import InvoiceCRUD
from CRUD.payments_crud import PaymentCRUD
from CRUD.loans_crud import LoanCRUD  # 引入 LoanCRUD 以处理逾期借阅费用
from CRUD.constants import InvoiceStatus


class InvoiceService:
    def __init__(self, db_connection):
        self.conn = db_connection
        self.invoice_crud = InvoiceCRUD(db_connection)
        self.payment_crud = PaymentCRUD(db_connection)
        self.loan_crud = LoanCRUD(db_connection)  # 初始化 LoanCRUD

    def generate_late_fee_invoice(self, user_id: int) -> Tuple[bool, Union[int, str]]:
        """Generate a late fee invoice based on overdue loans"""
        overdue_loans = self.loan_crud.get_overdue_loans_by_user(user_id)
        if not overdue_loans:
            return False, "The user has no overdue loan records"

        total_late_fee = sum(loan['late_fee'] for loan in overdue_loans)
        if total_late_fee <= 0:
            return False, "There is no overdue late fee to be paid"

        return self.invoice_crud.create(user_id, total_late_fee, "Overdue loan late fee")

    def get_user_invoices(self, user_id: int, include_paid: bool = False) -> List[Dict]:
        """Get the user's invoice list"""
        invoices = (self.invoice_crud.get_by_user(user_id) if include_paid
                    else self.invoice_crud.get_unpaid_by_user(user_id))

        for inv in invoices:
            payments = self.payment_crud.get_by_invoice(inv['invoice_id'])
            total_paid = sum(p['amount'] for p in payments)

            inv.update({
                'paid_amount': total_paid,
                'outstanding_amount': max(0, inv['amount'] - total_paid),
                'payment_status': "Paid" if total_paid >= inv['amount'] else "Unpaid"
            })

        return invoices

    def mark_invoice_as_paid(self, invoice_id: int) -> Tuple[bool, str]:
        """Mark the invoice as paid (including the transaction)"""
        try:
            with transaction(self.conn):
                # Check if it has been fully paid
                total_paid = self.payment_crud.get_total_paid(invoice_id)
                invoice = self.invoice_crud.get_invoice(invoice_id)

                if not invoice:
                    return False, "The invoice does not exist"
                if total_paid < invoice['amount']:
                    return False, "It has not been fully paid and cannot be marked as paid"

                return self.invoice_crud.mark_as_paid(invoice_id)
        except Exception as e:
            return False, f"Marking failed: {str(e)}"