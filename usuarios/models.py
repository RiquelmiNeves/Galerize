from django.db import models
from django.contrib.auth.models import User
class Foto(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)
    imagem = models.ImageField(upload_to='fotos/', blank=True, null=True)
    tags = models.CharField(max_length=255, blank=True, null=True, help_text="Separe as tags por vírgulas")
    data_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo