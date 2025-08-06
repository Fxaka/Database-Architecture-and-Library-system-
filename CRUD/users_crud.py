from typing import Tuple, Union, List, Dict
from DATABASE.transaction import transaction  # 显式导入transaction

class UserCRUD:
    def __init__(self, db_connection):
        self.conn = db_connection  # 确保变量名一致（原错误使用了self.com）

    def create_user(self, name: str, contact: str, user_type_id: int) -> Tuple[bool, Union[int, str]]:
        """创建用户（已移除冗余圆括号）"""
        sql = """INSERT INTO users(name, contact, user_type_id)
                 VALUES (%s, %s, %s) RETURNING user_id"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, (name, contact, user_type_id))
                user_id = cursor.fetchone()[0]
                self.conn.commit()
                return True, user_id  # 移除冗余圆括号
        except Exception as e:
            self.conn.rollback()
            return False, str(e)  # 移除冗余圆括号

    def get_user(self, user_id):
        """Get single user with type info - returns user dict or None"""
        sql = """SELECT u.*, t.type_name, t.max_borrowings, t.max_borrowing_days
                 FROM users u
                 JOIN user_types t ON u.user_type_id = t.type_id
                 WHERE u.user_id = %s"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, (user_id,))
                columns = [desc[0] for desc in cursor.description]
                user = cursor.fetchone()
                return dict(zip(columns, user)) if user else None


        except Exception as e:
            print("User query error:", e)
            return None

    def get_all_users(self):
        """Get all users with type info - returns list of users"""
        sql = """SELECT u.*, t.type_name, t.max_borrowings
                 FROM users u
                 JOIN user_types t ON u.user_type_id = t.type_id
                 ORDER BY u.user_id"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql)
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            print("User list query error:", e)
            return []

    def update_user(self, user_id, name=None, contact=None, user_type_id=None):
        """Update user - returns (success_status, affected_rows/error_message)"""
        updates = []
        params = []

        if name is not None:
            updates.append("name = %s")
            params.append(name)
        if contact is not None:
            updates.append("contact = %s")
            params.append(contact)
        if user_type_id is not None:
            updates.append("user_type_id = %s")
            params.append(user_type_id)

        if not updates:
            return (False, "No update fields provided")

        params.append(user_id)
        sql = f"UPDATE users SET {', '.join(updates)} WHERE user_id = %s"

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql, params)
                self.conn.commit()
                return (True, cursor.rowcount)
        except Exception as e:
            self.conn.rollback()
            return (False, str(e))

    def delete_user(self, user_id: int) -> Tuple[bool, str]:
        """安全删除用户（修正事务和缩进）"""
        try:
            with transaction(self.conn):  # 使用正确的conn变量
                with self.conn.cursor() as cursor:
                    # 检查关联记录（修正字符串引号）
                    cursor.execute("""
                        SELECT 1 FROM loans
                        WHERE user_id = %s AND actual_return_date IS NULL
                        LIMIT 1
                    """, (user_id,))
                    if cursor.fetchone():
                        return False, "The user has a borrowed record that has not been returned"  # 移除冗余圆括号

                    # 级联删除（按正确顺序）
                    cursor.execute("""
                        DELETE FROM payments 
                        WHERE invoice_id IN (
                            SELECT invoice_id FROM invoices WHERE user_id = %s
                        )
                    """, (user_id,))
                    cursor.execute("DELETE FROM invoices WHERE user_id = %s", (user_id,))
                    cursor.execute("DELETE FROM reservations WHERE user_id = %s", (user_id,))
                    cursor.execute("DELETE FROM loans WHERE user_id = %s", (user_id,))
                    cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))

                    return True, "The user is deleted"  # 移除冗余圆括号
        except Exception as e:
            return False, str(e)  # 移除冗余圆括号

    def update_user_contact(self, user_id, new_contact):
        """更新用户联系信息"""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE users
                    SET contact = %s
                    WHERE user_id = %s
                """, (new_contact, user_id))
                self.conn.commit()
                return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error updating user contact: {str(e)}")
            return False
