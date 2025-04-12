from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from bson.objectid import ObjectId
from .models import Usuario, Chat, Arquivo, OpcaoMenu
from .forms import UsuarioRegistroForm, UsuarioLoginForm, ArquivoUploadForm
import uuid


class UsuarioService:
    @staticmethod
    def criar_usuario(nome, email, senha):
        """
        Cria um novo usuário e o retorna
        """
        user = Usuario.objects.create_user(
            email=email,
            nome=nome,
            senha=senha
        )
        return user
    
    @staticmethod
    def login(email, senha):
        """
        Autentica um usuário com as credenciais fornecidas
        """
        user = authenticate(email=email, password=senha)
        return user
    
    @staticmethod
    def logout(usuario_id):
        """
        Método para registro de logout
        """
        pass
    
    @staticmethod
    def deletar_usuario(usuario_id):
        try:
            usuario = Usuario.objects.get(id=usuario_id)
            usuario.delete()
            return True
        except Usuario.DoesNotExist:
            return False


def registro_view(request):
    if request.method == 'POST':
        form = UsuarioRegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            return redirect('login')
    else:
        form = UsuarioRegistroForm()
    
    return render(request, 'registro.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = UsuarioLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            senha = form.cleaned_data['senha']
            
            user = UsuarioService.login(email, senha)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                form.add_error(None, 'Credenciais inválidas')
    else:
        form = UsuarioLoginForm()
    
    return render(request, 'login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard_view(request):
    user = request.user
    chats = user.listar_chats()
    return render(request, 'dashboard.html', {'user': user, 'chats': chats})


@login_required
def upload_arquivo_view(request):
    if request.method == 'POST':
        form = ArquivoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            nome = form.cleaned_data['nome']
            arquivo_file = request.FILES['arquivo']
            tipo = form.cleaned_data.get('tipo', '')
            
            if not tipo:
                tipo = arquivo_file.content_type
            
            arquivo = Arquivo.objects.create(
                nome=nome,
                tipo=tipo,
                conteudo=arquivo_file.read()
            )
            
            chat = Chat.objects.create(
                usuario=request.user,
                arquivo=arquivo,
                titulo=f"Chat sobre {nome}"
            )
            
            return redirect('chat_detail', chat_id=chat.id)
    else:
        form = ArquivoUploadForm()
    
    return render(request, 'upload_arquivo.html', {'form': form})


@login_required
def chat_detail_view(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, usuario=request.user)
    opcoes = chat.listar_opcoes()
    
    if not chat.analise:
        chat.reanalizar_fake_news()
        chat.refresh_from_db()
    
    return render(request, 'chat_detail.html', {
        'chat': chat,
        'opcoes': opcoes
    })


@login_required
def reanalizar_view(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, usuario=request.user)
    chat.reanalizar_fake_news()
    
    return redirect('chat_detail', chat_id=chat.id)


@login_required
def selecionar_opcao_view(request, chat_id, opcao_id):
    chat = get_object_or_404(Chat, id=chat_id, usuario=request.user)
    resultado = chat.selecionar_opcao(opcao_id)
    
    return JsonResponse({'resultado': resultado})