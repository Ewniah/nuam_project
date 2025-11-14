"""
Formularios para el sistema de calificaciones tributarias
"""

from django import forms
from .models import CalificacionTributaria, InstrumentoFinanciero
from decimal import Decimal
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PerfilUsuario, Rol


class CalificacionTributariaForm(forms.ModelForm):
    class Meta:
        model = CalificacionTributaria
        fields = ['instrumento', 'metodo_ingreso', 'monto', 'factor', 'numero_dj', 'fecha_informe', 'observaciones', 'activo']
        widgets = {
            'instrumento': forms.Select(attrs={'class': 'form-select'}),
            'metodo_ingreso': forms.Select(attrs={'class': 'form-select'}),
            'monto': forms.TextInput(attrs={  # ← CAMBIADO de NumberInput a TextInput
                'class': 'form-control',
                'placeholder': 'Ingrese el monto sin puntos ni comas',
                'inputmode': 'numeric',  # Muestra teclado numérico en móviles
            }),
            'factor': forms.TextInput(attrs={  # ← CAMBIADO de NumberInput a TextInput
                'class': 'form-control',
                'placeholder': 'Ejemplo: 12.5 o 12,5',
            }),
            'numero_dj': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: 1922 o 1949'
            }),
            'fecha_informe': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Agregue cualquier observación relevante...'
            }),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    
    def clean(self):
        """Validación personalizada"""
        cleaned_data = super().clean()
        metodo = cleaned_data.get('metodo_ingreso')
        monto = cleaned_data.get('monto')
        factor = cleaned_data.get('factor')
        
        # Validar que se haya ingresado al menos uno
        if metodo == 'MONTO' and not monto:
            raise forms.ValidationError("Debe ingresar un monto cuando selecciona 'Ingreso por Monto'")
        
        if metodo == 'FACTOR' and not factor:
            raise forms.ValidationError("Debe ingresar un factor cuando selecciona 'Ingreso por Factor'")
        
        return cleaned_data


class InstrumentoFinancieroForm(forms.ModelForm):
    """Formulario para crear/editar instrumentos financieros"""
    
    class Meta:
        model = InstrumentoFinanciero
        fields = ['codigo_instrumento', 'nombre_instrumento', 'tipo_instrumento', 'activo']
        widgets = {
            'codigo_instrumento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: CMPC'}),
            'nombre_instrumento': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_instrumento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Acción, Bono'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CargaMasivaForm(forms.Form):
    """Formulario para carga masiva de archivos"""
    archivo = forms.FileField(
        label='Archivo CSV/Excel',
        help_text='Formato permitido: CSV o Excel (.xlsx)',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv,.xlsx'})
    )

class RegistroUsuarioForm(UserCreationForm):
    """Formulario para registro de nuevos usuarios"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label='Nombre',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Juan'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label='Apellido',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pérez'})
    )
    telefono = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678'})
    )
    departamento = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Finanzas'})
    )
    rol = forms.ModelChoiceField(
        queryset=Rol.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Seleccione el rol del usuario'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'usuario123'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar mensajes de ayuda
        self.fields['username'].help_text = 'Requerido. 150 caracteres o menos. Solo letras, números y @/./+/-/_'
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': '••••••••'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': '••••••••'})
    
    def clean_email(self):
        """Validar que el email no esté registrado"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return email