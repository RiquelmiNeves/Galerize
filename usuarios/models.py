from django.db import models
from django.contrib.auth.models import User

class Foto(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)
    imagem = models.ImageField(upload_to='fotos/', blank=True, null=True)
    data_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    foto_perfil = models.ImageField(
        upload_to='perfil/',
        default='perfil/perfil.png',
        blank=True
    )

    def __str__(self):
        return f"Perfil de {self.user.first_name}"
