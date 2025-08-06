from guizero import App, Box, Text, TextBox, PushButton, ListBox, Window, yesno, error, info, Combo
from DATABASE.database import Database
from CRUD.users_crud import UserCRUD
from CRUD.materials_crud import MaterialCRUD
from CRUD.loans_crud import LoanCRUD
from CRUD.constants import MaterialStatus
from datetime import datetime

from GUI.loan import OverdueGUI
from SERVICES.loan_service import LoanService
from SERVICES.reservation_service import ReservationService




class LibraryBorrowSystem:
    def __init__(self):
        # Initialize database connection
        self.db = Database()
        self.conn = self.db.connect()

        if not self.conn:
            error("Error", "Database connection failed")
            return

        # Initialize CRUD operations
        self.user_crud = UserCRUD(self.conn)
        self.material_crud = MaterialCRUD(self.conn)
        self.loan_crud = LoanCRUD(self.conn)
        self.reservation_service = ReservationService(self.conn)  # Ensure this line exists

        # Create main window
        self.app = App(title="Library Borrowing System",
                       width=1000,
                       height=700,
                       layout="grid")

        # Create UI components
        self.create_widgets()

        # Initial data load
        self.refresh_user_list()
        self.refresh_material_list()

        self.app.display()

    def create_widgets(self):
        """Create all GUI components"""
        # Header
        Text(self.app, text="Library Borrowing System", size=20, grid=[0, 0, 2, 1])

        # User management area
        user_mgmt_box = Box(self.app, grid=[0, 1], width=450, height=350, border=True)
        Text(user_mgmt_box, text="User Management", size=14)

        # Add user button (will show the form when clicked)
        self.show_add_user_button = PushButton(user_mgmt_box, text="Add New User", command=self.show_add_user_form)

        # Add user section (initially hidden)
        self.add_user_box = Box(user_mgmt_box, width="fill", layout="grid", visible=False)
        Text(self.add_user_box, text="Add New User:", grid=[0, 0, 2, 1])

        Text(self.add_user_box, text="Name:", grid=[0, 1], align="left")
        self.new_user_name = TextBox(self.add_user_box, grid=[1, 1], width=30, align="left")

        Text(self.add_user_box, text="Email:", grid=[0, 2], align="left")
        self.new_user_email = TextBox(self.add_user_box, grid=[1, 2], width=30, align="left")

        Text(self.add_user_box, text="User Type:", grid=[0, 3], align="left")
        self.new_user_type = Combo(self.add_user_box, grid=[1, 3], options=["Student", "Teacher", "Staff"],
                                   selected="Student", align="left")

        # Buttons for the form
        button_box = Box(self.add_user_box, grid=[0, 4, 2, 1], width="fill")
        PushButton(button_box, text="Submit", align="left", command=self.add_user)
        PushButton(button_box, text="Cancel", align="left", command=self.hide_add_user_form)

        # User search and list section
        user_list_box = Box(user_mgmt_box, width="fill")
        Text(user_list_box, text="User List", size=12)

        # User search
        search_user_box = Box(user_list_box, width="fill")
        Text(search_user_box, text="Search:", align="left")
        self.user_search_input = TextBox(search_user_box, width=30, align="left")
        PushButton(search_user_box, text="Search", align="left",
                   command=self.search_user)
        PushButton(search_user_box, text="Refresh", align="left",
                   command=self.refresh_user_list)

        # User list
        self.user_list = ListBox(
            user_list_box,
            width="fill",
            height=150,
            scrollbar=True,
            items=[]
        )
        self.user_list.update_command(self.on_user_select)

        # Delete user button
        user_btn_box = Box(user_list_box, width="fill", layout="grid")
        self.delete_user_button = PushButton(user_btn_box, text="Delete", grid=[0, 0],
                                             command=self.delete_user, enabled=False)
        PushButton(user_btn_box, text="Details", grid=[1, 0],
                   command=self.show_user_details, enabled=True)
        self.edit_user_button = PushButton(user_btn_box, text="Edit", grid=[2, 0],
                                           command=self.edit_user_details, enabled=False)

        # Material selection area
        material_box = Box(self.app, grid=[1, 1], width=450, height=350, border=True)
        Text(material_box, text="Material Management", size=14)

        # Add material button
        self.show_add_material_button = PushButton(material_box, text="Add New Material",
                                                   command=self.show_add_material_form)

        # Add material section (initially hidden)
        self.add_material_box = Box(material_box, width="fill", layout="grid", visible=False)
        Text(self.add_material_box, text="Add New Material:", grid=[0, 0, 2, 1])

        Text(self.add_material_box, text="Name:", grid=[0, 1], align="left")
        self.new_material_name = TextBox(self.add_material_box, grid=[1, 1], width=30, align="left")

        Text(self.add_material_box, text="Author:", grid=[0, 2], align="left")
        self.new_material_author = TextBox(self.add_material_box, grid=[1, 2], width=30, align="left")

        Text(self.add_material_box, text="Type:", grid=[0, 3], align="left")
        self.new_material_type = Combo(self.add_material_box, grid=[1, 3],
                                       options=["Book", "Journal", "Magazine", "Thesis", "Audio Book"],
                                       selected="Book", align="left")

        Text(self.add_material_box, text="Publisher:", grid=[0, 4], align="left")
        self.new_material_publisher = TextBox(self.add_material_box, grid=[1, 4], width=30, align="left")

        Text(self.add_material_box, text="Pub Date:", grid=[0, 5], align="left")
        self.new_material_pubdate = TextBox(self.add_material_box, grid=[1, 5], width=30, align="left")

        Text(self.add_material_box, text="Price:", grid=[0, 6], align="left")
        self.new_material_price = TextBox(self.add_material_box, grid=[1, 6], width=30, align="left")

        # Buttons for the form
        button_box = Box(self.add_material_box, grid=[0, 7, 2, 1], width="fill", align="right")
        PushButton(button_box, text="Submit", align="left", command=self.add_material)
        PushButton(button_box, text="Cancel", align="left", command=self.hide_add_material_form)

        # Material search and list section
        material_list_box = Box(material_box, width="fill")
        Text(material_list_box, text="Material List", size=12)

        # Material search
        search_material_box = Box(material_list_box, width="fill")
        Text(search_material_box, text="Search:", align="left")
        self.material_search_input = TextBox(search_material_box, width=30, align="left")
        PushButton(search_material_box, text="Search", align="left",
                   command=self.search_material)
        PushButton(search_material_box, text="Refresh", align="left",
                   command=self.refresh_material_list)

        # Material list
        self.material_list = ListBox(
            material_list_box,
            width="fill",
            height=150,
            scrollbar=True,
            items=[]
        )
        self.material_list.update_command(self.on_material_select)

        # Material operation buttons
        material_btn_box = Box(material_list_box, width="fill", layout="grid")
        self.delete_material_button = PushButton(material_btn_box, text="Delete", grid=[0, 0],
                                                 command=self.delete_material, enabled=False)
        PushButton(material_btn_box, text="Details", grid=[1, 0],
                   command=self.show_material_details, enabled=True)
        self.edit_material_button = PushButton(material_btn_box, text="Edit", grid=[2, 0],
                                               command=self.edit_material_details, enabled=False)

        # Borrowing information area
        info_box = Box(self.app, grid=[0, 2, 2, 1], width=700, height=300, border=True)
        Text(info_box, text="Borrowing Information", size=14)

        # Selected items info
        self.selected_user_text = Text(info_box, text="Current User: Not selected", size=10)
        self.selected_user_loans = Text(info_box, text="Current Loans: None", size=10)
        self.selected_material_text = Text(info_box, text="Current Material: Not selected", size=10)
        self.selected_material_status = Text(info_box, text="", size=10)

        # Action buttons
        button_box = Box(info_box, width='fill',layout="grid")
        button_width = 10  # 你可以根据需要调整宽度
        button_height = 1  # 你可以根据需要调整高度
        self.borrow_button = PushButton(button_box, text="Borrow", grid=[1, 0], command=self.borrow_material,
                                        enabled=False)
        self.reserve_button = PushButton(button_box, text="Reserve", grid=[2, 0], command=self.reserve_material,
                                         enabled=False)
        self.return_button = PushButton(button_box, text="Return", grid=[3, 0], command=self.return_material,
                                        enabled=False, width=button_width, height=button_height)
        self.cancel_reservation_button = PushButton(button_box, text="Cancel Reservation", grid=[4, 0],
                                                    command=self.cancel_reservation, enabled=False)
        self.overdue_button = PushButton(button_box, text="Overdue Information", grid=[5, 0],
                                         command=self.show_overdue_information,
                                         enabled=True)
        PushButton(button_box, text="Clear Selection", grid=[6, 0], command=self.clear_selection, width=button_width, height=button_height)
        PushButton(button_box, text="Exit", grid=[4, 1], command=self.app.destroy, width=button_width, height=button_height)

    def show_add_user_form(self):
        """Show the add user form"""
        self.show_add_user_button.visible = False
        self.add_user_box.visible = True

    def hide_add_user_form(self):
        """Hide the add user form"""
        self.show_add_user_button.visible = True
        self.add_user_box.visible = False
        # Clear the form fields
        self.new_user_name.value = ""
        self.new_user_email.value = ""
        self.new_user_type.value = "Student"

    def show_add_material_form(self):
        """Show the add material form"""
        self.show_add_material_button.visible = False
        self.add_material_box.visible = True

    def hide_add_material_form(self):
        """Hide the add material form"""
        self.show_add_material_button.visible = True
        self.add_material_box.visible = False
        # Clear the form fields
        self.new_material_name.value = ""
        self.new_material_author.value = ""
        self.new_material_type.value = "Book"

    def refresh_user_list(self):
        """Refresh user list"""
        self.user_list.clear()
        users = self.user_crud.get_all_users()

        for user in users:
            display = f"{user['user_id']:03d} | {user['name']:20} | {user['type_name']}"
            self.user_list.append(display)

    def refresh_material_list(self):
        """Refresh materials list"""
        self.material_list.clear()
        materials = self.material_crud.get_all_materials()

        for material in materials:
            status = MaterialStatus(material['status']).name.replace('_', ' ').title()
            display = f"{material['material_id']} | {material['material_name']:30} | {material['author']} | {status}"
            self.material_list.append(display)

    def search_user(self):
        """Search users"""
        keyword = self.user_search_input.value.strip()
        if not keyword:
            self.refresh_user_list()
            return

        users = self.user_crud.get_all_users()
        found = [u for u in users if keyword.lower() in u['name'].lower() or
                 keyword == str(u['user_id'])]

        self.user_list.clear()
        if found:
            for user in found:
                display = f"{user['user_id']:03d} | {user['name']:20} | {user['type_name']}"
                self.user_list.append(display)
        else:
            info("Info", "No matching users found")

    def search_material(self):
        """Search materials"""
        keyword = self.material_search_input.value.strip()
        if not keyword:
            self.refresh_material_list()
            return

        materials = self.material_crud.get_all_materials()
        found = [m for m in materials if keyword.lower() in m['material_name'].lower() or
                 keyword == str(m['material_id']) or
                 keyword.lower() in m['author'].lower()]

        self.material_list.clear()
        if found:
            for material in found:
                status = MaterialStatus(material['status']).name.replace('_', ' ').title()
                display = f"{material['material_id']} | {material['material_name']:30} | {material['author']} | {status}"
                self.material_list.append(display)
        else:
            info("Info", "No matching materials found")

    def on_user_select(self, selected_value):
        """User selection event"""
        if not selected_value:
            return

        try:
            user_id = int(selected_value.split("|")[0].strip())
            user = self.user_crud.get_user(user_id)
            if user:
                self.selected_user = user
                self.selected_user_text.value = f"Current User: {user['name']} (ID: {user['user_id']}, Type: {user['type_name']})"

                # Get current loans
                active_loans = self.loan_crud.get_active_loans_by_user(user_id)
                current_materials = []
                for loan in active_loans:
                    material = self.material_crud.get_material(loan['material_id'])
                    if material:
                        current_materials.append(
                            f"{material['material_name']} (Material ID: {material['material_id']})")

                # Get current reservations
                reservations = self.reservation_service.get_user_reservations(user_id)
                reserved_materials = []
                for reservation in reservations:
                    material = self.material_crud.get_material(reservation['material_id'])
                    if material:
                        reserved_materials.append(
                            f"{material['material_name']} (Material ID: {material['material_id']})")

                # Update display
                current_materials_str = ', '.join(current_materials) if current_materials else 'None'
                reserved_materials_str = ', '.join(reserved_materials) if reserved_materials else 'None'
                self.selected_user_loans.value = (
                    f"Current Loans ({len(active_loans)}): {current_materials_str}\n"
                    f"Reserved Materials ({len(reservations)}): {reserved_materials_str}"
                )

                self.check_borrow_button()
                self.delete_user_button.enabled = True
                self.edit_user_button.enabled = True
            else:
                error("Error", "User not found")
        except Exception as e:
            error("Error", f"Failed to get user information: {str(e)}")

    def on_material_select(self, selected_value):
        """Material selection event"""
        if not selected_value:
            return

        try:
            material_id = int(selected_value.split("|")[0].strip())
            material = self.material_crud.get_material(material_id)
            if material:
                self.selected_material = material
                self.selected_material_text.value = f"Current Material: {material['material_name']} (ID: {material['material_id']}, Author: {material['author']})"
                self.check_borrow_button()
                self.delete_material_button.enabled = True
                self.edit_material_button.enabled = True
            else:
                error("Error", "Material not found")
        except Exception as e:
            error("Error", f"Failed to get material information: {str(e)}")

    def clear_selection(self):
        """Clear selections"""
        if hasattr(self, 'selected_user'):
            del self.selected_user
        if hasattr(self, 'selected_material'):
            del self.selected_material

        self.selected_user_text.value = "Current User: Not selected"
        self.selected_user_loans.value = "Current Loans: None\nReserved Materials: None"
        self.selected_material_text.value = "Current Material: Not selected"
        self.borrow_button.enabled = False
        self.reserve_button.enabled = False
        self.delete_user_button.enabled = False
        self.delete_material_button.enabled = False
        self.selected_reservation = None

    def add_user(self):
        """Add a new user to the system"""
        name = self.new_user_name.value.strip()
        email = self.new_user_email.value.strip()
        user_type = self.new_user_type.value

        if not name:
            error("Error", "Please enter a name")
            return
        if not email:
            error("Error", "Please enter an email")
            return

        # Map user type to type_id
        type_map = {"Student": 1, "Teacher": 2, "Staff": 3}
        type_id = type_map.get(user_type, 1)

        try:
            success = self.user_crud.create_user(name, email, type_id)
            if success:
                self.conn.commit()
                info("Success", f"User {name} added successfully!")
                self.hide_add_user_form()
                self.refresh_user_list()
            else:
                self.conn.rollback()
                error("Error", "Failed to add user")
        except Exception as e:
            self.conn.rollback()
            error("Error", f"Database error: {str(e)}")

    def add_material(self):
        """Add a new material to the system"""
        name = self.new_material_name.value.strip()
        author = self.new_material_author.value.strip()
        publisher = self.new_material_publisher.value.strip()
        pub_date = self.new_material_pubdate.value.strip()
        price = self.new_material_price.value.strip()
        material_type = self.new_material_type.value

        # Validate required fields
        if not all([name, author, publisher, pub_date, price]):
            error("Error", "All fields are required")
            return

        # Validate price format
        try:
            price = float(price)
        except ValueError:
            error("Error", "Invalid price format")
            return

        # Validate date format
        try:
            datetime.strptime(pub_date, "%Y-%m-%d")
        except ValueError:
            error("Error", "Invalid date format (YYYY-MM-DD required)")
            return

        # Type mapping
        type_map = {
            "Book": 1,
            "Journal": 2,
            "Magazine": 3,
            "Thesis": 4,
            "Audio Book": 5
        }
        type_id = type_map.get(material_type, 1)

        try:
            success, material_id = self.material_crud.create_material(
                name=name,
                author=author,
                publisher=publisher,
                material_type_id=type_id,
                publication_date=pub_date,
                price=price,
                status=MaterialStatus.AVAILABLE.value
            )
            if success:
                self.conn.commit()
                info("Success", f"Material {name} added successfully! ID: {material_id}")
                self.hide_add_material_form()
                self.refresh_material_list()
            else:
                self.conn.rollback()
                error("Error", "Failed to add material")
        except Exception as e:
            self.conn.rollback()
            error("Error", f"Database error: {str(e)}")

    def delete_user(self):
        """Delete the selected user"""
        if not hasattr(self, 'selected_user'):
            error("Error", "No user selected")
            return

        user_id = self.selected_user['user_id']
        user_name = self.selected_user['name']

        # Check if user has active loans
        active_loans = self.loan_crud.get_active_loans_by_user(user_id)
        if active_loans:
            error("Error", f"Cannot delete user {user_name} - they have active loans")
            return

        # Confirm deletion
        if yesno("Confirm", f"Are you sure you want to delete user {user_name} (ID: {user_id})?"):
            try:
                success = self.user_crud.delete_user(user_id)
                if success:
                    self.conn.commit()
                    info("Success", f"User {user_name} deleted successfully")
                    self.clear_selection()
                    self.refresh_user_list()
                else:
                    self.conn.rollback()
                    error("Error", "Failed to delete user")
            except Exception as e:
                self.conn.rollback()
                error("Error", f"Database error: {str(e)}")

    def delete_material(self):
        """Delete the selected material"""
        if not hasattr(self, 'selected_material'):
            error("Error", "No material selected")
            return

        material_id = self.selected_material['material_id']
        material_name = self.selected_material['material_name']

        if self.selected_material.get('status_name') == "Borrowed":
            error("Error", f"Cannot delete {material_name} - currently borrowed")
            return

        if yesno("Confirm", f"Delete {material_name} (ID: {material_id})?"):
            try:
                success = self.material_crud.delete_material(material_id)
                if success:
                    self.conn.commit()
                    info("Success", f"Material {material_name} deleted")
                    self.clear_selection()
                    self.refresh_material_list()
                else:
                    self.conn.rollback()
                    error("Error", "Delete failed")
            except Exception as e:
                self.conn.rollback()
                error("Error", f"Database error: {str(e)}")

    def borrow_material(self):
        """Borrow the selected material for the selected user"""
        if not hasattr(self, 'selected_user') or not hasattr(self, 'selected_material'):
            error("Error", "Please select both a user and a material")
            return

        user_id = self.selected_user['user_id']
        material_id = self.selected_material['material_id']
        user_type_id = self.selected_user['user_type_id']

        try:
            # Use the LoanCRUD's create_loan method which handles all the rules
            success, result = self.loan_crud.create_loan(user_id, material_id, user_type_id)

            if success:
                self.conn.commit()
                info("Success", f"Material borrowed successfully! Loan ID: {result}")
                self.refresh_material_list()  # Refresh to show the material is now borrowed
            else:
                self.conn.rollback()
                error("Error", f"Borrow failed: {result}")
        except Exception as e:
            self.conn.rollback()
            error("Error", f"Database error: {str(e)}")

    def show_user_details(self):
        """Show user details"""
        if not hasattr(self, 'selected_user'):
            error("Error", "Please select a user first")
            return

        user = self.selected_user
        user_id = user['user_id']

        # Get user loan count
        active_loans = self.loan_crud.get_active_loans_by_user(user_id)
        loan_count = len(active_loans)

        # Get user reservation count
        reservations = self.reservation_service.get_user_reservations(user_id)
        reservation_count = len(reservations)

        # Create user details information
        user_info = (
            f"User ID: {user['user_id']}\n"
            f"Name: {user['name']}\n"
            f"Type: {user['type_name']}\n"
            f"Contact: {user['contact']}\n"
            f"Current Loans: {loan_count}\n"
            f"Current Reservations: {reservation_count}\n"
            f"max_borrowings:{user.get('max_borrowings')}\n"
            f"max_borrowing_days:{user.get('max_borrowing_days')}"
        )

        # Display user details popup
        info("User Details", user_info)

    def edit_user_details(self):
        """Edit user contact information"""
        if not hasattr(self, 'selected_user'):
            error("Error", "Please select a user first")
            return

        user_id = self.selected_user['user_id']
        current_contact = self.selected_user['contact']

        # Create edit user contact window
        edit_window = Window(self.app, title="Edit User Contact", width=300, height=150)
        Text(edit_window, text="Edit User Contact", size=12)

        # Show current contact
        Text(edit_window, text="Current Contact:", size=10)
        self.current_contact_display = Text(edit_window, text=current_contact, size=10)

        # Input new contact
        Text(edit_window, text="New Contact:", size=10)
        self.new_contact_input = TextBox(edit_window, width=30)

        # Buttons
        button_box = Box(edit_window, width="fill")
        PushButton(button_box, text="Save", align="left", command=self.save_user_contact)
        PushButton(button_box, text="Cancel", align="left", command=edit_window.destroy)

    def edit_material_details(self):
        """Edit material price"""
        if not hasattr(self, 'selected_material'):
            error("Error", "Please select a material first")
            return

        material_id = self.selected_material['material_id']
        current_price = self.selected_material['price']

        # Create edit material price window
        edit_window = Window(self.app, title="Edit Material Price", width=300, height=150)
        Text(edit_window, text="Edit Material Price", size=12)

        # Show current price
        Text(edit_window, text="Current Price:", size=10)
        self.current_price_display = Text(edit_window, text=f"${current_price:.2f}", size=10)

        # Input new price
        Text(edit_window, text="New Price:", size=10)
        self.new_price_input = TextBox(edit_window, width=30)

        # Buttons
        button_box = Box(edit_window, width="fill")
        PushButton(button_box, text="Save", align="left", command=self.save_material_price)
        PushButton(button_box, text="Cancel", align="left", command=edit_window.destroy)

    def save_material_price(self):
        """Save material price changes"""
        new_price = self.new_price_input.value.strip()
        if not new_price:
            error("Error", "Please enter a new price")
            return

        try:
            new_price = float(new_price)
        except ValueError:
            error("Error", "Invalid price format")
            return

        material_id = self.selected_material['material_id']

        try:
            success = self.material_crud.update_material_price(material_id, new_price)
            if success:
                self.conn.commit()
                info("Success", "Material price updated successfully")
                self.clear_selection()
                self.refresh_material_list()
            else:
                self.conn.rollback()
                error("Error", "Failed to update material price")
        except Exception as e:
            self.conn.rollback()
            error("Error", f"Database error: {str(e)}")

    def save_user_contact(self):
        """Save user contact changes"""
        new_contact = self.new_contact_input.value.strip()
        if not new_contact:
            error("Error", "Please enter a new contact")
            return

        user_id = self.selected_user['user_id']

        try:
            success = self.user_crud.update_user_contact(user_id, new_contact)
            if success:
                self.conn.commit()
                info("Success", "User contact updated successfully")
                self.clear_selection()
                self.refresh_user_list()
            else:
                self.conn.rollback()
                error("Error", "Failed to update user contact")
        except Exception as e:
            self.conn.rollback()
            error("Error", f"Database error: {str(e)}")

    def show_material_details(self):
        """Show material details"""
        if not hasattr(self, 'selected_material'):
            error("Error", "Please select a material first")
            return

        material = self.selected_material
        status = MaterialStatus(material['status']).name.replace('_', ' ').title()

        details = (
            f"Material ID: {material['material_id']}\n"
            f"Name: {material['material_name']}\n"
            f"Author: {material['author']}\n"
            f"Type: {material['type_name']}\n"
            f"Publisher: {material['publisher']}\n"
            f"Publication Date: {material['publication_date']}\n"
            f"Price: ${material['price']:.2f}\n"
            f"Status: {status}"
        )
        info("Material Details", details)

    def cancel_reservation(self):
        """Cancel the reservation for the selected material"""
        if not hasattr(self, 'selected_user') or not hasattr(self, 'selected_material'):
            error("Error", "Please select both a user and a material")
            return

        user_id = self.selected_user['user_id']
        material_id = self.selected_material['material_id']

        try:
            # Get user reservations
            reservations = self.reservation_service.get_user_reservations(user_id)
            reservation_to_cancel = None
            for reservation in reservations:
                if reservation['material_id'] == material_id:
                    reservation_to_cancel = reservation
                    break

            if not reservation_to_cancel:
                error("Error", "No reservation found for this material")
                return

            # Confirm cancellation
            if yesno("Confirm", f"Cancel reservation for {self.selected_material['material_name']}?"):
                success, message = self.reservation_service.cancel_reservation(reservation_to_cancel['reservation_id'])
                if success:
                    info("Success", message)
                    self.refresh_material_list()
                    self.on_user_select(f"{self.selected_user['user_id']} | {self.selected_user['name']}")
                else:
                    error("Error", message)
        except Exception as e:
            error("Error", f"Failed to cancel reservation: {str(e)}")

    def reserve_material(self):
        """Reserve the selected material for the selected user"""
        if not hasattr(self, 'selected_user') or not hasattr(self, 'selected_material'):
            error("Error", "Please select both a user and a material")
            return

        user_id = self.selected_user['user_id']
        material_id = self.selected_material['material_id']

        try:
            # Use the ReservationService to handle the reservation
            success, message = self.reservation_service.make_reservation(user_id, material_id)
            if success:
                info("Success", message)
                self.refresh_material_list()
                self.on_user_select(f"{self.selected_user['user_id']} | {self.selected_user['name']}")
            else:
                error("Error", message)
        except Exception as e:
            error("Error", f"Reservation failed: {str(e)}")

    def return_material(self):
        """Return the selected material"""
        if not hasattr(self, 'selected_user'):
            error("Error", "Please select a user first")
            return

        if not hasattr(self, 'selected_material'):
            error("Error", "Please select a material first")
            return

        user_id = self.selected_user['user_id']
        material_id = self.selected_material['material_id']

        # Get active loan for this user and material
        active_loans = self.loan_crud.get_active_loans_by_user(user_id)
        loan_to_return = None

        for loan in active_loans:
            if loan['material_id'] == material_id:
                loan_to_return = loan
                break

        if not loan_to_return:
            error("Error", "This user hasn't borrowed the selected material")
            return

        # Confirm return
        if yesno("Confirm", f"Return {self.selected_material['material_name']} borrowed by {self.selected_user['name']}?"):
            try:
                # Use the LoanService to handle the return
                loan_service = LoanService(self.conn)
                success, message = loan_service.return_material(loan_to_return['loan_id'])

                if success:
                    info("Success", message)
                    self.refresh_material_list()
                    self.on_user_select(f"{self.selected_user['user_id']} | {self.selected_user['name']}")
                else:
                    error("Error", message)
            except Exception as e:
                error("Error", f"Return failed: {str(e)}")

    def check_borrow_button(self):
        """Check borrow, reserve and return button states"""
        user_selected = hasattr(self, 'selected_user')
        material_selected = hasattr(self, 'selected_material')

        self.borrow_button.enabled = user_selected and material_selected
        self.reserve_button.enabled = user_selected and material_selected

        # Enable return button only if user has borrowed the selected material
        self.return_button.enabled = False
        self.cancel_reservation_button.enabled = False  # Disable cancel reservation button by default
        if user_selected and material_selected:
            user_id = self.selected_user['user_id']
            material_id = self.selected_material['material_id']
            active_loans = self.loan_crud.get_active_loans_by_user(user_id)
            for loan in active_loans:
                if loan['material_id'] == material_id:
                    self.return_button.enabled = True
                    break

            # Check if the user has a reservation for this material
            reservations = self.reservation_service.get_user_reservations(user_id)
            for reservation in reservations:
                if reservation['material_id'] == material_id:
                    self.cancel_reservation_button.enabled = True
                    break

    def clear_selection(self):
        """Clear selections"""
        if hasattr(self, 'selected_user'):
            del self.selected_user
        if hasattr(self, 'selected_material'):
            del self.selected_material

        self.selected_user_text.value = "Current User: Not selected"
        self.selected_user_loans.value = "Current Loans: None\nReserved Materials: None"
        self.selected_material_text.value = "Current Material: Not selected"
        self.borrow_button.enabled = False
        self.reserve_button.enabled = False
        self.return_button.enabled = False
        self.cancel_reservation_button.enabled = False
        self.delete_user_button.enabled = False
        self.delete_material_button.enabled = False

    def show_overdue_information(self):
        """Show overdue information window"""
        self.app.hide()  # 改为隐藏而不是销毁
        overdue_app = OverdueGUI()
        # 设置返回按钮的回调
        overdue_app.return_button.config(command=lambda: self.return_from_overdue(overdue_app))
        overdue_app.app.display()

    def return_from_overdue(self, overdue_app):
        """Return from overdue interface"""
        overdue_app.app.destroy()
        self.app.show()

if __name__ == "__main__":
    LibraryBorrowSystem()