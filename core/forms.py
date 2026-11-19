from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db import transaction

from core.models import Profile


class LoginForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    login = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean_login(self):
        login = self.cleaned_data.get('login')
        if not login:
            raise forms.ValidationError("This field is required.")
        return login

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError("This field is required.")
        return password


class RegisterForm(forms.ModelForm):
    nickname = forms.CharField(max_length=40, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'nickname', 'password']
        labels = {
            'username': 'Login',
            'email': 'Email',
            'nickname': 'NickName',
            'password': 'Password',
            'password_confirm': 'Repeat Password',
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Passwords do not match!")
        return cleaned_data

    def save(self, commit=True):
        data = self.cleaned_data.copy()
        nickname = data.pop('nickname')
        data.pop('password_confirm')

        if not commit:
            user = User(**data)
            user.set_password(data['password'])
            return user

        data.pop('password')
        with transaction.atomic():
            user = User.objects.create_user(
                password=self.cleaned_data['password'],
                **data,
            )
            Profile.objects.create(user=user, nickname=nickname)
        return user

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError("This field is required.")
        user = User(
            username=self.data.get('username'),
            email=self.data.get('email'),
        )
        validate_password(password, user=user)
        return password

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError("This field is required.")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("This field is required.")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

class ProfileForm(forms.ModelForm):
    login = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = Profile
        fields = ['login', 'email', 'nickname', 'avatar']
        labels = {
            'login': 'Login',
            'email': 'Email',
            'nickname': 'Nickname',
            'avatar': 'Avatar',
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user_id:
            self.fields['login'].initial = self.instance.user.username
            self.fields['email'].initial = self.instance.user.email
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def clean_login(self):
        login = self.cleaned_data.get('login')
        if not login:
            raise forms.ValidationError("This field is required.")
        if User.objects.filter(username=login).exclude(
                pk=self.instance.user_id
        ).exists():
            raise forms.ValidationError("This login is already taken.")
        return login

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("This field is required.")
        if User.objects.filter(email=email).exclude(
                pk=self.instance.user_id
        ).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean_nickname(self):
        nickname = self.cleaned_data.get('nickname')
        if not nickname:
            raise forms.ValidationError("This field is required.")
        if Profile.objects.filter(nickname=nickname).exclude(
                pk=self.instance.pk
        ).exists():
            raise forms.ValidationError("This nickname is already taken.")
        return nickname

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
            extension = '.' + avatar.name.rsplit('.', 1)[-1].lower()
            if extension not in allowed_extensions:
                raise forms.ValidationError(
                    "Avatar must be a JPG, JPEG, PNG, or GIF image."
                )
            if avatar.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Avatar file size must be under 2MB.")
        return avatar

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.user.username = self.cleaned_data['login']
        profile.user.email = self.cleaned_data['email']
        if commit:
            profile.user.save()
            profile.save()
        return profile