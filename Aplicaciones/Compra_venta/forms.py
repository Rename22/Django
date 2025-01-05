from django import forms
from .models import Usuario

class RegistroUsuarioForm(forms.ModelForm):
    confirmar_contrasena = forms.CharField(widget=forms.PasswordInput, label="Confirmar Contraseña")

    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'cedula', 'direccion', 'telefono', 'correo', 'contrasena']

        widgets = {
            'contrasena': forms.PasswordInput,  # Esto mantiene el campo de contraseña oculto
        }

    def clean(self):
        cleaned_data = super().clean()
        contrasena = cleaned_data.get("contrasena")
        confirmar_contrasena = cleaned_data.get("confirmar_contrasena")

        if contrasena != confirmar_contrasena:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data
