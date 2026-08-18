from django.contrib import admin

from .models import RoomType, CheckInSession, Booking

# Реєструємо їх в адмінці
admin.site.register(RoomType)
admin.site.register(CheckInSession)
admin.site.register(Booking)

