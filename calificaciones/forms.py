from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import CalificacionTributaria, InstrumentoFinanciero, Rol


class CalificacionTributariaForm(forms.ModelForm):
    """Formulario completo para crear/editar Calificaciones Tributarias con 30 factores"""
    
    class Meta:
        model = CalificacionTributaria
        fields = '__all__'
        exclude = ['usuario_creador', 'fecha_creacion', 'fecha_modificacion', 'metodo_ingreso', 'factor']
        
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
            'secuencia': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '10 dígitos'
            }),
            'numero_dividendo': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '10 dígitos'
            }),
            'tipo_sociedad': forms.Select(attrs={
                'class': 'form-select'
            }),
            'valor_historico': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.0001'
            }),
            'mercado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: ACN',
                'maxlength': '3'
            }),
            'ejercicio': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Año (4 dígitos)'
            }),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones adicionales...'
            }),
            'monto': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Ej: 1000000.00'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        
        labels = {
            'instrumento': 'Instrumento Financiero',
            'numero_dj': 'Número DJ',
            'fecha_informe': 'Fecha del Informe',
            'secuencia': 'Secuencia',
            'numero_dividendo': 'N° Dividendo',
            'tipo_sociedad': 'Tipo Sociedad',
            'valor_historico': 'Valor Histórico',
            'mercado': 'Mercado',
            'ejercicio': 'Ejercicio',
            'observaciones': 'Observaciones',
            'monto': 'Monto Base / Total',
            'activo': 'Activo'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Agregar widgets y labels para todos los factores 8-37
        for i in range(8, 38):
            field_name = f'factor_{i}'
            self.fields[field_name].widget = forms.NumberInput(attrs={
                'class': 'form-control factor-input',
                'placeholder': '0.00000000',
                'step': '0.00000001',
                'min': '0',
                'max': '1'
            })
            self.fields[field_name].label = f'Factor {i}'
            self.fields[field_name].required = False
    
    def clean(self):
        """Validación: al menos un factor debe ser ingresado"""
        cleaned_data = super().clean()
        
        # Verificar que al menos un factor 8-37 tenga valor > 0
        factores = [cleaned_data.get(f'factor_{i}') or 0 for i in range(8, 38)]
        
        if not any(f > 0 for f in factores):
            raise forms.ValidationError(
                'Debe ingresar al menos un factor mayor que 0'
            )
        
        return cleaned_data


class InstrumentoFinancieroForm(forms.ModelForm):
    """Formulario para crear/editar Instrumentos Financieros"""
    
    class Meta:
        model = InstrumentoFinanciero
        fields = ['codigo_instrumento', 'nombre_instrumento', 'tipo_instrumento', 'activo']
        widgets = {
            'codigo_instrumento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Opcional - Se generará automáticamente si se deja vacío',
                'required': False
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
    """Formulario de registro de usuario con campos adicionales y perfil"""
    email = forms.EmailField(
        required=True,
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'nombre@ejemplo.com'
        })
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label='Nombre',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su nombre'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label='Apellido',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su apellido'
        })
    )
    telefono = forms.CharField(
        max_length=20,
        required=False,
        label='Teléfono',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+56 9 1234 5678'
        })
    )
    departamento = forms.CharField(
        max_length=100,
        required=False,
        label='Departamento',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Finanzas, Operaciones'
        })
    )
    rol = forms.ModelChoiceField(
        queryset=Rol.objects.all(),
        required=True,
        label='Rol',
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        help_text='Seleccione el rol que mejor describe su función'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: jsmith'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Agregar clases de Bootstrap a todos los campos
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ej: jsmith'
        })
        self.fields['username'].help_text = 'Solo letras, números y @/./+/-/_'
        
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '••••••••'
        })
        self.fields['password1'].label = 'Contraseña'
        self.fields['password1'].help_text = 'Mínimo 8 caracteres, no solo numérica'
        
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '••••••••'
        })
        self.fields['password2'].label = 'Confirmar Contraseña'
        self.fields['password2'].help_text = ''
    
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
    Formulario simplificado para ingreso de calificaciones con factores 8-16.
    Permite ingresar factores directamente con validación automática.
    """
    
    class Meta:
        model = CalificacionTributaria
        fields = [
            'instrumento',
            'numero_dj',
            'fecha_informe',
            'factor_8',
            'factor_9',
            'factor_10',
            'factor_11',
            'factor_12',
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
            'factor_8': forms.NumberInput(attrs={
                'class': 'form-control factor-input',
                'placeholder': '0.00000000',
                'step': '0.00000001',
                'min': '0',
                'max': '1'
            }),
            'factor_9': forms.NumberInput(attrs={
                'class': 'form-control factor-input',
                'placeholder': '0.00000000',
                'step': '0.00000001',
                'min': '0',
                'max': '1'
            }),
            'factor_10': forms.NumberInput(attrs={
                'class': 'form-control factor-input',
                'placeholder': '0.00000000',
                'step': '0.00000001',
                'min': '0',
                'max': '1'
            }),
            'factor_11': forms.NumberInput(attrs={
                'class': 'form-control factor-input',
                'placeholder': '0.00000000',
                'step': '0.00000001',
                'min': '0',
                'max': '1'
            }),
            'factor_12': forms.NumberInput(attrs={
                'class': 'form-control factor-input',
                'placeholder': '0.00000000',
                'step': '0.00000001',
                'min': '0',
                'max': '1'
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
            'factor_8': 'Factor 8 (Con crédito IDPC ≥ 01.01.2017)',
            'factor_9': 'Factor 9 (Con crédito IDPC ≤ 31.12.2016)',
            'factor_10': 'Factor 10',
            'factor_11': 'Factor 11',
            'factor_12': 'Factor 12',
            'observaciones': 'Observaciones',
            'activo': 'Activo'
        }
    
    def clean(self):
        """Validación: al menos un factor debe ser ingresado y suma <= 1"""
        cleaned_data = super().clean()
        
        factores = [
            cleaned_data.get('factor_8') or 0,
            cleaned_data.get('factor_9') or 0,
            cleaned_data.get('factor_10') or 0,
            cleaned_data.get('factor_11') or 0,
            cleaned_data.get('factor_12') or 0,
        ]
        
        # Verificar que al menos un factor sea mayor que 0
        if not any(f > 0 for f in factores):
            raise forms.ValidationError(
                'Debe ingresar al menos un factor mayor que 0'
            )
        
        return cleaned_data


class AdminUserCreationForm(UserCreationForm):
    """Formulario administrativo para crear usuarios con asignación de grupo/rol"""
    
    email = forms.EmailField(
        required=True,
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'usuario@empresa.cl'
        })
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label='Nombre',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre completo'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label='Apellido',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellidos'
        })
    )
    rol = forms.ModelChoiceField(
        queryset=Rol.objects.all(),
        required=True,
        label='Rol del Sistema',
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        help_text='Administrador: acceso completo | Analista Financiero: CRUD | Auditor: solo lectura'
    )
    telefono = forms.CharField(
        max_length=20,
        required=False,
        label='Teléfono (opcional)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+56 9 1234 5678'
        })
    )
    departamento = forms.CharField(
        max_length=100,
        required=False,
        label='Departamento (opcional)',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Finanzas, TI'
        })
    )
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        label='Cuenta Activa',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Desmarcar para crear cuenta desactivada'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario único'
            })
        }
        labels = {
            'username': 'Nombre de Usuario'
        }
    
    def save(self, commit=True):
        """Guarda usuario y crea perfil con rol asignado"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_active = self.cleaned_data['is_active']
        
        if commit:
            user.save()
            
            # Crear perfil de usuario con rol
            from .models import PerfilUsuario
            PerfilUsuario.objects.create(
                user=user,
                rol=self.cleaned_data['rol'],
                telefono=self.cleaned_data.get('telefono', ''),
                departamento=self.cleaned_data.get('departamento', '')
            )
        
        return user


class AdminUserEditForm(forms.ModelForm):
    """Formulario administrativo para editar usuarios existentes"""
    
    rol = forms.ModelChoiceField(
        queryset=Rol.objects.all(),
        required=True,
        label='Rol del Sistema',
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    telefono = forms.CharField(
        max_length=20,
        required=False,
        label='Teléfono',
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    departamento = forms.CharField(
        max_length=100,
        required=False,
        label='Departamento',
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo Electrónico',
            'is_active': 'Cuenta Activa'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'perfilusuario'):
            self.fields['rol'].initial = self.instance.perfilusuario.rol
            self.fields['telefono'].initial = self.instance.perfilusuario.telefono
            self.fields['departamento'].initial = self.instance.perfilusuario.departamento
    
    def save(self, commit=True):
        """Guarda usuario y actualiza perfil"""
        user = super().save(commit=commit)
        
        if commit and hasattr(user, 'perfilusuario'):
            user.perfilusuario.rol = self.cleaned_data['rol']
            user.perfilusuario.telefono = self.cleaned_data.get('telefono', '')
            user.perfilusuario.departamento = self.cleaned_data.get('departamento', '')
            user.perfilusuario.save()
        
        return user
