from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import ValidationError

from club.models import Boat, Role


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


class MemberCreationForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(label="E-mail")
    phone = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "type": "tel",
                "placeholder": "+01 234567890"
            }
        ),
        required=True
    )

    class Meta(UserCreationForm.Meta):  # type: ignore
        model = get_user_model()
        fields = (
            "username",
            "first_name",
            "last_name",
            "role",
            "email",
            "phone",
            "phone_visibility",
            "password1",
            "password2",
            "sailing_permission",
            "avatar",
        )
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        if not (
            self.user.is_authenticated              # type: ignore
            and self.user.role                      # type: ignore
            and self.user.role.management_rights    # type: ignore
        ):
            self.fields.pop("role")

    def clean_phone(self):
        return validate_phone_number(self.cleaned_data["phone"])

    def save(self):
        obj = super().save(commit=False)

        if (
            "role" not in self.fields
            and not self.user.is_authenticated      # type: ignore
        ):
            obj.role = Role.objects.get(name="Member")

        obj.save()
        return obj


class MemberUpdateForm(UserChangeForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(label="E-mail")
    phone = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "type": "tel",
                "placeholder": "+01 234567890"
            }
        ),
        required=True
    )

    class Meta(UserCreationForm.Meta):  # type: ignore
        model = get_user_model()
        fields = (
            "username",
            "first_name",
            "last_name",
            "role",
            "email",
            "phone",
            "phone_visibility",
            "sailing_permission",
            "avatar",
        )
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        if not (
            self.user.role                          # type: ignore
            and self.user.role.management_rights    # type: ignore
        ):
            self.fields.pop("role")

    def clean_phone(self):
        return validate_phone_number(self.cleaned_data["phone"])


def validate_phone_number(phone: str):
    prefix, *number = phone.split(" ")
    valid = []
    valid.append(prefix[0] == "+")
    valid.append(prefix[1:].isnumeric())
    valid.append(all(number[i].isnumeric() for i in range(len(number))))

    if not all(valid):
        raise ValidationError("Phone number must be in format: +01 234567890")
    
    return phone
