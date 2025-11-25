from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import CalificacionTributaria, InstrumentoFinanciero, Rol


class CalificacionTributariaForm(forms.ModelForm):
    """Formulario para crear/editar Calificaciones Tributarias"""
    
    class Meta:
        model = CalificacionTributaria
        fields = [
            'instrumento',
            'metodo_ingreso',
            'monto',
            'factor',
            'numero_dj',
            'fecha_informe',
            'observaciones',
            'activo'
        ]
        widgets = {
            'instrumento': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'metodo_ingreso': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'monto': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 5.000.000',
                'step': '0.0001'
            }),
            'factor': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 5.00000000',
                'step': '0.00000001'
            }),
            'numero_dj': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 1949 o 1922'
            }),
            'fecha_informe': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales...'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'instrumento': 'Instrumento Financiero',
            'metodo_ingreso': 'Método de Ingreso',
            'monto': 'Monto (CLP)',
            'factor': 'Factor',
            'numero_dj': 'Número DJ',
            'fecha_informe': 'Fecha del Informe',
            'observaciones': 'Observaciones',
            'activo': 'Activo'
        }

    def clean(self):
        """Validación personalizada: requiere monto O factor según método"""
        cleaned_data = super().clean()
        metodo = cleaned_data.get('metodo_ingreso')
        monto = cleaned_data.get('monto')
        factor = cleaned_data.get('factor')

        if metodo == 'MONTO' and not monto:
            raise forms.ValidationError('Debe ingresar un monto cuando el método es "Ingreso por Monto"')
        
        if metodo == 'FACTOR' and not factor:
            raise forms.ValidationError('Debe ingresar un factor cuando el método es "Ingreso por Factor"')

        return cleaned_data


class InstrumentoFinancieroForm(forms.ModelForm):
    """Formulario para crear/editar Instrumentos Financieros"""
    
    class Meta:
        model = InstrumentoFinanciero
        fields = ['codigo_instrumento', 'nombre_instrumento', 'tipo_instrumento', 'activo']
        widgets = {
            'codigo_instrumento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: CMPC, BCHILE',
                'required': True
            }),
            'nombre_instrumento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Empresas CMPC S.A.',
                'required': True
            }),
            'tipo_instrumento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Acción, Bono, Fondo Mutuo',
                'required': True
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'codigo_instrumento': 'Código del Instrumento',
            'nombre_instrumento': 'Nombre del Instrumento',
            'tipo_instrumento': 'Tipo de Instrumento',
            'activo': 'Activo'
        }


class CargaMasivaForm(forms.Form):
    """Formulario para carga masiva de archivos CSV/Excel"""
    archivo = forms.FileField(
        label='Archivo',
        help_text='Formatos permitidos: CSV, XLSX',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv,.xlsx'
        })
    )

    def clean_archivo(self):
        """Valida que el archivo sea CSV o XLSX"""
        archivo = self.cleaned_data.get('archivo')
        
        if archivo:
            nombre = archivo.name.lower()
            if not (nombre.endswith('.csv') or nombre.endswith('.xlsx')):
                raise forms.ValidationError('Solo se permiten archivos CSV o XLSX')
            
            # Validar tamaño (máximo 10 MB)
            if archivo.size > 10 * 1024 * 1024:
                raise forms.ValidationError('El archivo no puede superar los 10 MB')
        
        return archivo


class RegistroForm(UserCreationForm):
    """Nuevo: Formulario de registro de usuario con campos adicionales"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label='Nombre',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label='Apellido',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Usuario'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar clases de Bootstrap a los campos de contraseña
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
    
    def clean_email(self):
        """Valida que el email no esté registrado"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado')
        return email


# ==========================================
# NUEVO: Formulario Simple de Factores (Demo)
# ==========================================

class CalificacionFactoresSimpleForm(forms.ModelForm):
    """
    Formulario simplificado para ingreso de calificaciones con 5 factores.
    Permite ingresar montos y calcular factores automáticamente.
    """
    
    class Meta:
        model = CalificacionTributaria
        fields = [
            'instrumento',
            'numero_dj',
            'fecha_informe',
            'monto_8',
            'monto_9',
            'monto_10',
            'monto_11',
            'monto_12',
            'observaciones',
            'activo'
        ]
        widgets = {
            'instrumento': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'numero_dj': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 1949 o 1922'
            }),
            'fecha_informe': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'monto_8': forms.NumberInput(attrs={
                'class': 'form-control monto-input',
                'placeholder': '0.00',
                'step': '0.0001',
                'min': '0',
                'data-factor': '8'
            }),
            'monto_9': forms.NumberInput(attrs={
                'class': 'form-control monto-input',
                'placeholder': '0.00',
                'step': '0.0001',
                'min': '0',
                'data-factor': '9'
            }),
            'monto_10': forms.NumberInput(attrs={
                'class': 'form-control monto-input',
                'placeholder': '0.00',
                'step': '0.0001',
                'min': '0',
                'data-factor': '10'
            }),
            'monto_11': forms.NumberInput(attrs={
                'class': 'form-control monto-input',
                'placeholder': '0.00',
                'step': '0.0001',
                'min': '0',
                'data-factor': '11'
            }),
            'monto_12': forms.NumberInput(attrs={
                'class': 'form-control monto-input',
                'placeholder': '0.00',
                'step': '0.0001',
                'min': '0',
                'data-factor': '12'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales...'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'instrumento': 'Instrumento Financiero',
            'numero_dj': 'Número DJ',
            'fecha_informe': 'Fecha del Informe',
            'monto_8': 'Monto Factor 8 (Con crédito IDPC ≥ 01.01.2017)',
            'monto_9': 'Monto Factor 9 (Con crédito IDPC ≤ 31.12.2016)',
            'monto_10': 'Monto Factor 10',
            'monto_11': 'Monto Factor 11',
            'monto_12': 'Monto Factor 12',
            'observaciones': 'Observaciones',
            'activo': 'Activo'
        }
    
    def clean(self):
        """Validación: al menos un monto debe ser ingresado"""
        cleaned_data = super().clean()
        
        montos = [
            cleaned_data.get('monto_8'),
            cleaned_data.get('monto_9'),
            cleaned_data.get('monto_10'),
            cleaned_data.get('monto_11'),
            cleaned_data.get('monto_12'),
        ]
        
        # Verificar que al menos un monto sea mayor que 0
        if not any(m and m > 0 for m in montos):
            raise forms.ValidationError(
                'Debe ingresar al menos un monto mayor que 0'
            )
        
        return cleaned_data
