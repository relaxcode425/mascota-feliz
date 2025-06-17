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
    
    from django import forms
from .models import ServicioDomicilio

class ServicioDomicilioForm(forms.ModelForm):
    class Meta:
        model = ServicioDomicilio
        fields = ['num_estilistas', 'num_veterinarios', 'horario_asignado', 'descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'horario_asignado': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        e = cleaned_data.get('num_estilistas')
        v = cleaned_data.get('num_veterinarios')

        if e and v:
            raise forms.ValidationError("No pueden ir estilistas y veterinarios al mismo tiempo.")
        if (e not in [1, 2] and v not in [1, 2]):
            raise forms.ValidationError("Debe haber 1 o 2 estilistas o 1 o 2 veterinarios.")
