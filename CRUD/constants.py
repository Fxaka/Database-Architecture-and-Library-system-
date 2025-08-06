from enum import IntEnum

class MaterialStatus(IntEnum):
    UNKNOWN = 0  # 必须添加的基础状态
    AVAILABLE = 1
    BORROWED = 2
    RESERVED = 3

class LoanStatus(IntEnum):
    ACTIVE = 1
    RETURNED = 2
    OVERDUE = 3

class InvoiceStatus(IntEnum):
    UNPAID = 1
    PAID = 2

class ReservationStatus(IntEnum):
    ACTIVE = 1
    CANCELLED = 2
    COMPLETED = 3

class UserType(IntEnum):
    STUDENT = 1
    TEACHER = 2
    STAFF = 3

