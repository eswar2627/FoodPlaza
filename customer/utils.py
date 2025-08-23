from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime

def send_order_status_update(order_id, status):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'order_{order_id}',
        {
            'type': 'order_status_update',
            'status': status,
            'timestamp': datetime.utcnow().isoformat(),
        }
    )
