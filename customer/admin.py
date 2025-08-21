from django.contrib import admin
from .models import MenuItem, Category, OrderModel
from django.utils.safestring import mark_safe

@admin.register(OrderModel)
class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ['map_location']

    def map_location(self, obj):
        if obj.latitude and obj.longitude:
            return mark_safe(
                f'<iframe src="https://maps.google.com/maps?q={obj.latitude},{obj.longitude}&z=15&output=embed" width="100%" height="300"></iframe>'
            )
        return "Location not set"

    map_location.short_description = "Delivery Location"


admin.site.register(MenuItem)
admin.site.register(Category)
