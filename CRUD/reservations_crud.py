from datetime import datetime
from typing import Tuple, Union, List, Dict


class ReservationCRUD:
    def __init__(self, db_connection):
        self.conn = db_connection

    def create(self, user_id: int, material_id: int) -> Tuple[bool, Union[int, str]]:
        """Create a new reservation
        Args:
            user_id: ID of the user making reservation
            material_id: ID of material to reserve

        Returns:
            (success, reservation_id/error_message)
        """
        sql = """INSERT INTO reservations(user_id, material_id, reservation_date, status)
                 VALUES (%s, %s, %s, %s) RETURNING reservation_id"""
        try:
            with self.conn.cursor() as cursor:
                # Check material availability first
                cursor.execute("SELECT status FROM materials WHERE material_id=%s", (material_id,))
                if cursor.fetchone()[0] != 1:  # 1=Available
                    return (False, "Material not available for reservation")

                cursor.execute(sql, (user_id, material_id, datetime.now(), 1))  # 1=Active
                res_id = cursor.fetchone()[0]

                # Update material status to Reserved (3)
                cursor.execute("UPDATE materials SET status=3 WHERE material_id=%s", (material_id,))

                self.conn.commit()
                return (True, res_id)
        except Exception as e:
            self.conn.rollback()
            return (False, str(e))

    def cancel(self, reservation_id: int) -> Tuple[bool, str]:
        """Cancel a reservation
        Args:
            reservation_id: ID of reservation to cancel

        Returns:
            (success, message)
        """
        try:
            with self.conn.cursor() as cursor:
                # Get associated material ID
                cursor.execute(
                    "SELECT material_id FROM reservations WHERE reservation_id=%s",
                    (reservation_id,)
                )
                material_id = cursor.fetchone()[0]

                # Delete reservation
                cursor.execute(
                    "DELETE FROM reservations WHERE reservation_id=%s",
                    (reservation_id,)
                )

                # Revert material status to Available (1)
                cursor.execute(
                    "UPDATE materials SET status=1 WHERE material_id=%s",
                    (material_id,)
                )

                self.conn.commit()
                return (True, "Reservation cancelled successfully")
        except Exception as e:
            self.conn.rollback()
            return (False, f"Failed to cancel reservation: {str(e)}")

    def get_active_by_user(self, user_id: int) -> List[Dict]:
        """Get all active reservations for a user
        Args:
            user_id: ID of the user

        Returns:
            List of reservation records with material details
        """
        sql = """SELECT r.reservation_id, r.reservation_date, 
                        m.material_id, m.material_name, m.author
                 FROM reservations r
                 JOIN materials m ON r.material_id = m.material_id
                 WHERE r.user_id=%s AND r.status=1
                 ORDER BY r.reservation_date"""
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (user_id,))
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]