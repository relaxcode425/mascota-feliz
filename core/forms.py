from django import forms
from django.contrib.auth import get_user_model
from .models import Dueno

User = get_user_model()

class DuenoForm(forms.ModelForm):
    username = forms.CharField(label="Nombre de usuario")
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField()

    class Meta:
        model = Dueno
        fields = ['rut', 'nombre', 'contacto', 'direccion', 'username', 'password', 'email']
    
    def save(self, commit=True):
        # 1. Crear el usuario (cliente)
        usuario = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email'],
            tipo_usuario='cliente'
        )

        # 2. Crear el dueño asociado al usuario
        dueno = super().save(commit=False)
        dueno.usuario = usuario

        if commit:
            dueno.save()

        return dueno