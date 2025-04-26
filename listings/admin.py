from django.contrib import admin
from django.utils.safestring import mark_safe  
from .models import Car
from .models import UserPreference

# customize how Car objects appear in the django admin
class CarAdmin(admin.ModelAdmin):
    # show these fields in the list view
    list_display = ('make', 'model', 'year', 'mileage', 'image_tag')
    # make the image preview read-only
    readonly_fields = ('image_tag',)

    # method to display a small image preview in admin
    def image_tag(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" />')  # safely render the image tag
        return "No Image"

    image_tag.short_description = 'Image'  # label for the admin interface

# register car model with custom admin settings
admin.site.register(Car, CarAdmin)

# register UserPreference model with default settings
admin.site.register(UserPreference)
