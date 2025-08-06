import datetime as dt_class
from typing import Tuple
from guizero import App, Box, Text, ListBox, Window, PushButton, yesno
from DATABASE.database import Database
from SERVICES.loan_service import LoanService
from SERVICES.payment_service import PaymentService
from CRUD.users_crud import UserCRUD
from CRUD.constants import MaterialStatus


class OverdueGUI:
    def __init__(self):
        # Initialize the database connection
        self.db = Database()
        self.conn = self.db.connect()
        self.loan_service = LoanService(self.conn)
        self.payment_service = PaymentService(self.conn)
        self.user_crud = UserCRUD(self.conn)

        # Store the currently selected user ID, material ID, loan ID, and late fee
        self.current_user_id = None
        self.current_material_id = None
        self.current_loan_id = None
        self.current_late_fee = 0.0

        # Create the main application window
        self.app = App(title="Overdue information inquiry", width=800, height=600)

        # Create the layout
        self.create_widgets()

        # Run the application
        self.app.display()

    def create_widgets(self):
        # Create the left and right layout boxes
        main_box = Box(self.app, layout="grid", border=1)
        left_box = Box(main_box, grid=[0, 0], width=400, height=600, border=1)
        right_box = Box(main_box, grid=[1, 0], width=500, height=600, border=1)

        # Create the top and bottom layout boxes on the right
        right_top_box = Box(right_box, layout="grid", width=500, height=300, border=1)
        right_bottom_box = Box(right_box, layout="grid", width=500, height=300, border=1)

        # Overdue user list
        Text(left_box, text="List of overdue users", grid=[0, 0])
        self.overdue_user_listbox = ListBox(left_box, grid=[0, 1], width=350, height=500, command=self.on_user_select)

        # Add a refresh button
        refresh_button = PushButton(left_box, text="Refresh", grid=[0, 2], command=self.refresh_overdue_users)

        # Overdue material list
        Text(right_top_box, text="List of overdue materials", grid=[0, 0])
        self.overdue_material_listbox = ListBox(right_top_box, grid=[0, 1], width=350, height=200,
                                                command=self.on_material_select)

        # Specific information of the overdue user
        Text(right_bottom_box, text="Specific information", grid=[0, 0])
        self.user_info_text = Text(right_bottom_box, text="Please select a user and \nan overdue material first", grid=[0, 1], width=40,
                                   height=7)

        # Payment button
        self.pay_button = PushButton(right_bottom_box, text="Pay overdue fees", grid=[0, 4], command=self.pay_overdue_fee)
        self.pay_button.disable()  # Disable the payment button initially

        # 返回按钮
        self.return_button = PushButton(right_bottom_box, text="Return", grid=[0, 5], command=self.return_to_main)

        # Initialize the overdue user list
        self.load_overdue_users()

    def refresh_overdue_users(self):
        """Refresh the list of overdue users"""
        self.overdue_user_listbox.clear()
        self.load_overdue_users()

    def load_overdue_users(self):
        # Get all overdue loan records
        overdue_loans = self.loan_service.get_overdue_loans()
        user_ids = set()
        for loan in overdue_loans:
            user_ids.add(loan['user_id'])

        # Get information about overdue users
        for user_id in user_ids:
            user = self.user_crud.get_user(user_id)
            if user:
                # Get the number of overdue materials for this user
                overdue_count = len(self.loan_service.get_overdue_loans_by_user(user_id))
                self.overdue_user_listbox.append(
                    f"{user['name']} (ID: {user['user_id']}) - Number of overdue materials: {overdue_count}")

    def on_user_select(self, selected_user):
        # Parse the user ID
        user_id = int(selected_user.split("(ID: ")[1].split(") - Number of overdue materials:")[0].strip())
        self.current_user_id = user_id

        # Load the overdue materials for this user
        self.load_overdue_materials(user_id)

        # Clear the user information text box
        self.user_info_text.value = "Please select an overdue material \nto view detailed information"
        self.current_material_id = None
        self.current_loan_id = None
        self.pay_button.disable()

    def load_overdue_materials(self, user_id):
        # Clear the overdue material list
        self.overdue_material_listbox.clear()

        # Get the overdue loan records for this user
        overdue_loans = self.loan_service.get_overdue_loans_by_user(user_id)
        for loan in overdue_loans:
            material_status_id = loan.get('material_status', MaterialStatus.UNKNOWN)
            material_status_str = MaterialStatus(material_status_id).name
            self.overdue_material_listbox.append(
                f"{loan['material_name']} (ID: {loan['material_id']}) Overdue for {loan['overdue_days']} days Status: {material_status_str}")

    def on_material_select(self, selected_material):
        if not self.current_user_id:
            return

        # Parse the material ID
        material_id = int(selected_material.split("(ID: ")[1].split(")")[0].strip())
        self.current_material_id = material_id

        # Load the detailed information of the user and the material
        self.load_user_material_info(self.current_user_id, material_id)

    def load_user_material_info(self, user_id, material_id):
        # Clear the user information text box
        self.user_info_text.value = ""

        # Get the specific information of the user
        user = self.user_crud.get_user(user_id)
        # Get all overdue loan records of this user
        overdue_loans = self.loan_service.get_overdue_loans_by_user(user_id)

        # Find the specific material record that was selected
        selected_loan = None
        for loan in overdue_loans:
            if loan['material_id'] == material_id:
                selected_loan = loan
                break

        if user and selected_loan:
            info_text = f"User ID: {user['user_id']}\n"
            info_text += f"Name: {user['name']}\n\n"

            self.current_loan_id = selected_loan['loan_id']
            success, self.current_late_fee, message = self.calculate_overdue_fee(self.current_loan_id)
            material_status_id = selected_loan.get('material_status', MaterialStatus.UNKNOWN)
            material_status_str = MaterialStatus(material_status_id).name

            info_text += f"Material ID: {selected_loan['material_id']}\n"
            info_text += f"Material name: {selected_loan['material_name']}\n"
            info_text += f"Number of overdue days: {selected_loan['overdue_days']}\n"

            if success:
                info_text += f"Overdue fee: {self.current_late_fee}\n"
                self.pay_button.enable()  # Enable the payment button when there is an overdue fee
            else:
                info_text += f"Overdue fee: Calculation failed - {message}\n"
                self.pay_button.disable()  # Disable the payment button when there is no overdue fee

            info_text += f"Material status: {material_status_str}\n"

            self.user_info_text.value = info_text

    def pay_overdue_fee(self):
        if not self.current_loan_id:
            self.user_info_text.value = "Please select a loan record to pay first"
            return

        print(f"Preparing to pay for loan ID: {self.current_loan_id}")

        # Confirmation dialog for payment
        confirm = yesno("Confirm payment", f"Are you sure you want to pay the overdue fee of {self.current_late_fee} yuan?")
        if confirm:
            print("User confirmed payment, starting the payment process...")

            try:
                # 1. Calculate the overdue fee (confirm again)
                success, fee, message = self.calculate_overdue_fee(self.current_loan_id)
                if not success:
                    print(f"Fee calculation failed: {message}")
                    self.user_info_text.value = f"Payment cannot be completed: {message}"
                    return

                print(f"Confirmed overdue fee: {fee} yuan")

                # 2. Call the payment service
                print("Calling the PaymentService to make the payment...")
                payment_service = PaymentService(self.conn)
                success, message = payment_service.pay_overdue_fee(self.current_loan_id)

                if success:
                    print("Payment successful!")
                    self.user_info_text.value = "Payment successful! \nThe overdue fee has been cleared."
                    self.pay_button.disable()

                    # Refresh the interface
                    if self.current_user_id:
                        self.load_overdue_materials(self.current_user_id)
                else:
                    print(f"Payment failed: {message}")
                    self.user_info_text.value = f"Payment failed: {message}"

            except Exception as e:
                print(f"An exception occurred during the payment process: {str(e)}")
                self.user_info_text.value = f"Payment error: {str(e)}"

    def calculate_overdue_fee(self, loan_id: int) -> Tuple[bool, float, str]:
        """Calculate the overdue fee"""
        try:
            # Get the loan record and user type
            loan_info = self.loan_service._get_loan_info(loan_id)
            print(f"Loan info: {loan_info}")  # Add log output
            if not loan_info:
                return False, 0.0, "Loan record does not exist"

            # Get the overdue fee rate rules
            rules = self.loan_service.get_borrowing_rules(loan_info['user_type_id'])
            print(f"Borrowing rules: {rules}")  # Add log output
            if not rules:
                return False, 0.0, "Unable to obtain the overdue fee rate rules"

            # Assume the overdue fee rate is the third element of the tuple
            late_fee_per_day = float(rules[2])  # Modify this line
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

    def return_to_main(self):
        """Return to the main interface"""
        # Destroy the current OverdueGUI window
        self.app.destroy()
        from GUI.Gui import LibraryBorrowSystem
        main_app = LibraryBorrowSystem()
        main_app.app.display()

if __name__ == "__main__":
    OverdueGUI()