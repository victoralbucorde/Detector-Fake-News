import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from djongo import models as djongo_models


class UsuarioManager(BaseUserManager):
    def create_user(self, email, nome, senha=None):
        if not email:
            raise ValueError('Usuários devem ter um email')
        
        user = self.model(
            email=self.normalize_email(email),
            nome=nome,
        )
        
        user.set_password(senha)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, nome, senha):
        user = self.create_user(
            email=email,
            nome=nome,
            senha=senha,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Usuario(AbstractBaseUser, PermissionsMixin):
    _id = djongo_models.ObjectIdField()
    id = djongo_models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = djongo_models.CharField(max_length=100)
    email = djongo_models.EmailField(max_length=255, unique=True)
    senhaHash = djongo_models.CharField(max_length=128)  # Armazenará a senha hash
    is_active = djongo_models.BooleanField(default=True)
    is_staff = djongo_models.BooleanField(default=False)
    is_admin = djongo_models.BooleanField(default=False)
    data_criacao = djongo_models.DateTimeField(auto_now_add=True)
    
    objects = UsuarioManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']
    
    def __str__(self):
        return self.email
    
    def criar_chat(self, arquivo):
        return Chat.objects.create(usuario=self, arquivo=arquivo)
    
    def listar_chats(self):
        return Chat.objects.filter(usuario=self.id)


class Arquivo(djongo_models.Model):
    _id = djongo_models.ObjectIdField()
    id = djongo_models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = djongo_models.CharField(max_length=255)
    tipo = djongo_models.CharField(max_length=50)
    conteudo = djongo_models.BinaryField()
    data_upload = djongo_models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nome


class OpcaoMenu(djongo_models.Model):
    _id = djongo_models.ObjectIdField()
    id = djongo_models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    descricao = djongo_models.CharField(max_length=255)
    icone = djongo_models.CharField(max_length=50, blank=True, null=True)
    ordem = djongo_models.IntegerField(default=0)
    
    def __str__(self):
        return self.descricao
    
    def exibir_informacao(self):
        return f"Opção: {self.descricao}"


class AnaliseEmbedded(djongo_models.Model):
    id = djongo_models.UUIDField(default=uuid.uuid4, editable=False)
    resultado = djongo_models.TextField()
    data_analise = djongo_models.DateTimeField(auto_now=True)
    pontuacao_confiabilidade = djongo_models.FloatField(default=0.0)
    categorias = djongo_models.JSONField(default=dict, blank=True)
    
    class Meta:
        abstract = True


class Chat(djongo_models.Model):
    _id = djongo_models.ObjectIdField()
    id = djongo_models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = djongo_models.ForeignKey(Usuario, on_delete=djongo_models.CASCADE)
    arquivo = djongo_models.ForeignKey(Arquivo, on_delete=djongo_models.CASCADE)
    data_criacao = djongo_models.DateTimeField(auto_now_add=True)
    ultima_interacao = djongo_models.DateTimeField(auto_now=True)
    titulo = djongo_models.CharField(max_length=255, blank=True, null=True)
    analise = djongo_models.EmbeddedField(
        model_container=AnaliseEmbedded,
        null=True, blank=True
    )
    
    def __str__(self):
        return f"Chat {self.id} - {self.usuario.nome}"
    
    def listar_opcoes(self):
        return OpcaoMenu.objects.all()
    
    def selecionar_opcao(self, id_opcao):
        try:
            opcao = OpcaoMenu.objects.get(id=id_opcao)
            return opcao.exibir_informacao()
        except OpcaoMenu.DoesNotExist:
            return "Opção não encontrada"
    
    def visualizar_arquivo(self):
        return self.arquivo
    
    def reanalizar_fake_news(self):
        if not self.analise:
            self.analise = AnaliseEmbedded(
                resultado="Analisando documento...",
                pontuacao_confiabilidade=0.0
            )
        else:
            self.analise.resultado = "Reanalisando documento..."
        
        self.save()
        return self.analise