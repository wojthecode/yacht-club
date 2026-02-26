from django import forms

from club.models import Boat


class BoatForm(forms.ModelForm):

    class Meta:
        model = Boat
        fields = "__all__"
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        if not (
            self.user.role                          # type:ignore
            and self.user.role.management_rights    # type:ignore
        ):
            self.fields.pop("owner")
            self.fields.pop("keeper")
            self.fields.pop("club_owner")

    def save(self):
        obj = super().save(commit=False)

        if "owner" not in self.fields:
            obj.owner = self.user

        obj.save()
        self.save_m2m()

        return obj
