from __future__ import annotations

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .i18n import translate
from .models import (
    MAX_COMMENT_LENGTH,
    MAX_DRINK_NAME_LENGTH,
    MAX_TAKE_LENGTH,
    Comment,
    Profile,
    Take,
)

User = get_user_model()


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, lang: str = "en", **kwargs):
        super().__init__(*args, **kwargs)
        self.lang = lang
        # Password fields must never round-trip through the browser/autocomplete.
        for name in ("password1", "password2"):
            if name in self.fields:
                self.fields[name].widget.attrs["autocomplete"] = "new-password"
        for field in self.fields.values():
            field.widget.attrs.setdefault("autocomplete", "off")

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(translate(self.lang, "username_taken"))
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(translate(self.lang, "email_taken"))
        return email

    def save(self, commit: bool = True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    identifier = forms.CharField(
        label="Email or username",
        widget=forms.TextInput(
            attrs={"autocomplete": "username", "autocapitalize": "none"}
        ),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )


class TakeForm(forms.Form):
    drink_name = forms.CharField(max_length=MAX_DRINK_NAME_LENGTH, required=True)
    content = forms.CharField(
        max_length=MAX_TAKE_LENGTH,
        required=True,
        widget=forms.Textarea(attrs={"rows": 5}),
    )

    def __init__(self, *args, lang: str = "en", **kwargs):
        super().__init__(*args, **kwargs)
        self.lang = lang
        self.fields["drink_name"].error_messages["required"] = translate(
            lang, "drink_name_required"
        )
        self.fields["drink_name"].error_messages["max_length"] = translate(
            lang, "drink_name_too_long"
        )
        self.fields["content"].error_messages["required"] = translate(
            lang, "content_too_short", limit=10
        )
        self.fields["content"].error_messages["max_length"] = translate(
            lang, "content_too_long", limit=MAX_TAKE_LENGTH
        )
        self.fields["drink_name"].widget.attrs.update(
            {
                "placeholder": translate(lang, "compose.drink_ph"),
                "maxlength": MAX_DRINK_NAME_LENGTH,
                "autocapitalize": "sentences",
            }
        )
        self.fields["content"].widget.attrs.update(
            {
                "placeholder": translate(lang, "compose.take_ph"),
                "maxlength": MAX_TAKE_LENGTH,
                "minlength": 10,
            }
        )

    def clean_drink_name(self):
        value = (self.cleaned_data.get("drink_name") or "").strip()
        if not value:
            raise forms.ValidationError(translate(self.lang, "drink_name_required"))
        return value

    def clean_content(self):
        value = (self.cleaned_data.get("content") or "").strip()
        if len(value) < 10:
            raise forms.ValidationError(
                translate(self.lang, "content_too_short", limit=10)
            )
        return value

    def to_take(self, author) -> Take:
        return Take(
            author=author,
            drink_name=self.cleaned_data["drink_name"],
            content=self.cleaned_data["content"],
        )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("content",)
        widgets = {"content": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, lang: str = "en", **kwargs):
        super().__init__(*args, **kwargs)
        self.lang = lang
        self.fields["content"].error_messages["required"] = translate(
            lang, "comment_empty"
        )
        self.fields["content"].error_messages["max_length"] = translate(
            lang, "comment_too_long", limit=MAX_COMMENT_LENGTH
        )

    def clean_content(self):
        value = (self.cleaned_data.get("content") or "").strip()
        if not value:
            raise forms.ValidationError(translate(self.lang, "comment_empty"))
        return value


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("display_name", "bio")
        widgets = {
            "display_name": forms.TextInput(attrs={"maxlength": 60}),
            "bio": forms.Textarea(attrs={"rows": 3, "maxlength": 280}),
        }
