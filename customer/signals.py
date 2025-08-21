# your_app_name/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Order
from channels.layers import get_channel_layer

@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    group_name = f'order_{instance.id}'

    # Broadcast the status update
    channel_layer.group_send(
        group_name,
        {
            'type': 'order_status_update',
            'status': instance.status
        }
    )
