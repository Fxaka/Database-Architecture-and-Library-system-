from typing import Tuple, List, Dict, Union
from DATABASE.transaction import transaction
from CRUD.reservations_crud import ReservationCRUD
from CRUD.materials_crud import MaterialCRUD
from CRUD.users_crud import UserCRUD
from CRUD.constants import MaterialStatus


class ReservationService:
    def __init__(self, db_connection):
        self.conn = db_connection
        self.reservation_crud = ReservationCRUD(db_connection)
        self.material_crud = MaterialCRUD(db_connection)
        self.user_crud = UserCRUD(db_connection)

    def make_reservation(self, user_id: int, material_id: int) -> Tuple[bool, str]:
        """创建预约（含事务）"""
        try:
            with transaction(self.conn):
                # 1. 验证用户
                if not self.user_crud.get_user(user_id):
                    return False, "The user does not exist"

                # 2. 验证资料
                material = self.material_crud.get_material(material_id)
                if not material:
                    return False, "The data does not exist"
                if material['status'] != MaterialStatus.AVAILABLE.value:
                    return False, "Reservations are not available at this time"

                # 3. 创建预约
                result = self.reservation_crud.create(user_id, material_id)
                if not result[0]:
                    return result

                return True, f"The appointment is successful, and the appointment ID is made: {result[1]}"
        except Exception as e:
            return False, f"The appointment failed: {str(e)}"

    def cancel_reservation(self, reservation_id: int) -> Tuple[bool, str]:
        """取消预约（含事务）"""
        return self.reservation_crud.cancel(reservation_id)

    def get_user_reservations(self, user_id: int) -> List[Dict]:
        """获取用户预约列表"""
        reservations = self.reservation_crud.get_active_by_user(user_id)
        for res in reservations:
            material = self.material_crud.get_material(res['material_id'])
            if material:
                res['material_details'] = material
        return reservations