from CRUD.constants import MaterialStatus
from typing import Tuple


class MaterialCRUD:
    def __init__(self, db_connection):
        self.conn = db_connection

        # Move the status mapping dictionary to class attributes
        self.STATUS_MAP = {
            1: "Available",
            2: "Borrowed",
            3: "Lost"
        }

    def create_material(self, name, author, publisher, material_type_id, publication_date, price, status):
        """Add new material - returns (success_status, material_id/error_message)"""
        sql = """INSERT INTO materials(material_name, author, publisher, type_id, publication_date, price, status)
                 VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING material_id"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, (name, author, publisher, material_type_id, publication_date, price, status))
                material_id = cursor.fetchone()[0]
                self.conn.commit()
                return (True, material_id)
        except Exception as e:
            self.conn.rollback()
            return (False, str(e))

    def get_material(self, material_id):
        """Get single material with type info - returns material dict or None"""
        sql = """SELECT m.*, t.type_name 
                 FROM materials m
                 JOIN material_types t ON m.type_id = t.type_id
                 WHERE m.material_id = %s"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, (material_id,))
                columns = [desc[0] for desc in cursor.description]
                material = cursor.fetchone()
                if material:
                    material = dict(zip(columns, material))
                    # Add the status name field
                    material["status_name"] = self.STATUS_MAP.get(material.get("status"), "Unknown")
                return material
        except Exception as e:
            print("Material query error:", e)
            return None

    def get_available_materials(self):
        """Get all available materials - returns list of materials"""
        sql = """SELECT m.*, t.type_name 
                 FROM materials m
                 JOIN material_types t ON m.type_id = t.type_id
                 WHERE m.status = %s
                 ORDER BY m.material_id"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, (MaterialStatus.AVAILABLE.value,))
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            print("Available materials query error:", e)
            return []

    def update_material(self, material_id: int, update_data: dict) -> Tuple[bool, str]:
        """
        Update material information in the database

        Args:
            material_id: ID of the material to update
            update_data: Dictionary of fields to update

        Returns:
            Tuple of (success, message)
        """
        try:
            cursor = self.conn.cursor()

            # Prepare the SET clause for the SQL update
            set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
            values = list(update_data.values())
            values.append(material_id)  # Add material_id for WHERE clause

            query = f"UPDATE materials SET {set_clause} WHERE material_id = %s"
            cursor.execute(query, values)
            self.conn.commit()

            return True, "Material updated successfully"
        except Exception as e:
            self.conn.rollback()
            return False, f"Failed to update material: {str(e)}"

    # New deletion method
    def delete_material(self, material_id):
        """Delete material by ID - returns (success_status, affected_rows/error_message)"""
        sql = "DELETE FROM materials WHERE material_id = %s"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, (material_id,))
                self.conn.commit()
                return (True, cursor.rowcount)
        except Exception as e:
            self.conn.rollback()
            return (False, str(e))

    def get_all_materials(self):
        """Get all materials regardless of status"""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                SELECT m.material_id, m.material_name, m.author, m.publisher, 
                       m.publication_date, m.price, m.status, 
                       mt.type_name
                FROM materials m
                JOIN material_types mt ON m.type_id = mt.type_id
                ORDER BY m.material_id
            """)
            columns = [desc[0] for desc in cursor.description]  # Get column names
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def update_material_price(self, material_id, new_price):
        """Update the material price"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE materials
                    SET price = %s
                    WHERE material_id = %s
                """, (new_price, material_id))
                self.conn.commit()
                return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error updating material price: {str(e)}")
            return False
