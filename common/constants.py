## common/constants.py
# User Roles
class Roles:
    USER = "user"
    ADMIN = "admin"
    ALL = {USER, ADMIN}

# Order Statuses
class OrderStatus:
    NEW = 'new'
    PROCESSING = 'processing'
    SHIPPING = 'shipping'
    DELIVERED = 'delivered'
    CANCELED = 'canceled'
    REJECTED = 'rejected'

    ALL = {NEW, PROCESSING, SHIPPING, DELIVERED, CANCELED, REJECTED}

# Order Status Transition Map
ORDER_TRANSITIONS = {
    OrderStatus.NEW: [OrderStatus.PROCESSING, OrderStatus.CANCELED, OrderStatus.REJECTED],
    OrderStatus.PROCESSING: [OrderStatus.SHIPPING, OrderStatus.REJECTED],
    OrderStatus.SHIPPING: [OrderStatus.DELIVERED],
    OrderStatus.DELIVERED: [],
    OrderStatus.CANCELED: [],
    OrderStatus.REJECTED: [],
}
