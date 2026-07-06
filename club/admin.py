from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin

from club.models import Boat, Member, Event, Role, SailingPermission, WorkTask


@admin.register(Member)
class MemberAdmin(UserAdmin):
    list_display = (
        "username", "first_name", "last_name", "role", "sailing_permission"
    )
    list_filter = ["role", ]
    add_fieldsets = (
        (
            (
                "User info",
                {
                    "fields": (
                        "username",
                        "email",
                        "password1",
                        "password2",
                    )
                }
            ),
            (
                "Additional info",
                {
                    "fields": (
                        "first_name",
                        "last_name",
                        "phone",
                        "phone_visibility",
                        "role",
                        "sailing_permission",
                        "avatar",
                    )
                },
            ),
        )
    )
    fieldsets = (
        (
            (
                "User info",
                {
                    "fields": (
                        "username",
                        "email",
                        "password",
                    )
                }
            ),
            (
                "Additional info",
                {
                    "fields": (
                        "first_name",
                        "last_name",
                        "phone",
                        "phone_visibility",
                        "role",
                        "sailing_permission",
                        "avatar",
                    )
                },
            ),
        )
    )


@admin.register(Role)
class AdminRole(admin.ModelAdmin):
    list_display = ("name", "management_rights")


@admin.register(SailingPermission)
class AdminSailingPermission(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Boat)
class AdminBoat(admin.ModelAdmin):
    list_display = ("name", "length", "club_owner")


@admin.register(Event)
class AdminEvent(admin.ModelAdmin):
    list_display  = ("name", "date", "created_by")


@admin.register(WorkTask)
class AdminWorkTask(admin.ModelAdmin):
    list_display  = ("name", "date", "created_by")


admin.site.unregister(Group)
