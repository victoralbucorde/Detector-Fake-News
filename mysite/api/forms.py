from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Arquivo, Chat


class UsuarioRegistroForm(UserCreationForm):
    """
    Formulário para registro de novos usuários estendendo o UserCreationForm do Django.
    """
    nome = forms.CharField(max_length=100, required=True,
                           widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Seu nome'}))
    email = forms.EmailField(required=True,
                            widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seu@email.com'}))
    
    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'password1', 'password2']
    
    def clean_email(self):
        """Validação personalizada para garantir email único"""
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email já está em uso. Por favor, use outro email.')
        return email


class UsuarioLoginForm(forms.Form):
    """
    Formulário para login de usuários existentes.
    """
    email = forms.EmailField(required=True,
                            widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seu@email.com'}))
    senha = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Sua senha'}))


class ArquivoUploadForm(forms.Form):
    """
    Formulário para upload de arquivos no sistema.
    """
    nome = forms.CharField(max_length=255, required=True,
                          widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do arquivo'}))
    arquivo = forms.FileField(required=True,
                             widget=forms.FileInput(attrs={'class': 'form-control'}))
    tipo = forms.CharField(max_length=50, required=False,
                          widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tipo do arquivo'}))
    
    def clean_arquivo(self):
        """Validação do arquivo enviado"""
        arquivo = self.cleaned_data.get('arquivo')
        # Você pode adicionar validações personalizadas aqui
        if arquivo and arquivo.size > 10 * 1024 * 1024:  # 10MB
            raise forms.ValidationError("O arquivo é muito grande. O tamanho máximo é 10MB.")
            
        return arquivo


class ChatForm(forms.Form):
    """
    Formulário para criar ou editar um chat.
    Adaptado para trabalhar com MongoDB e documentos embedded.
    """
    titulo = forms.CharField(max_length=255, required=False,
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título do chat'}))
    
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super(ChatForm, self).__init__(*args, **kwargs)
        
        if self.instance:
            self.fields['titulo'].initial = self.instance.titulo
    
    def save(self, commit=True):
        if not self.instance:
            # Criar novo chat não é feito normalmente por este formulário
            # mas por meio do upload de arquivo
            return None
        
        self.instance.titulo = self.cleaned_data['titulo']
        
        if commit:
            self.instance.save()
        
        return self.instance


class OpcaoMenuSelecaoForm(forms.Form):
    """
    Formulário para selecionar uma opção de menu.
    """
    opcao_id = forms.UUIDField(widget=forms.HiddenInput())