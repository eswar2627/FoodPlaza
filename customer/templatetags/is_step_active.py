# templatetags/is_step_active.py
from django import template

register = template.Library()

@register.filter
def is_step_active(order, step):
    steps_order = ['Pending', 'Confirmed', 'Preparing', 'Out for Delivery', 'Delivered']
    current_index = steps_order.index(order.status) if order.status in steps_order else -1
    step_index = steps_order.index(step) if step in steps_order else -1
    return step_index <= current_index
