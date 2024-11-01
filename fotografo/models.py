# fotografo/models.py

from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password

class Fotografo(models.Model):
    nome = models.CharField(max_length=100)
    senha = models.CharField(max_length=128)
    fone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(unique=True)

    def save(self, *args, **kwargs):
        if self.pk is None:  # Somente criptografa ao criar um novo registro
            self.senha = make_password(self.senha)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

class Ensaio(models.Model):
    descricao = models.TextField()
    val_ensaio = models.DecimalField(max_digits=10, decimal_places=2)
    qtd_fotos = models.IntegerField()
    pago = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(default=timezone.now)
    val_foto_extra = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    data_escolha = models.DateField(null=True, blank=True)
    foto_capa = models.ImageField(upload_to="capas_ensaios/", null=True, blank=True)
    fotografo = models.ForeignKey(Fotografo, on_delete=models.CASCADE, related_name="ensaios")
    total_fotos_escolhidas = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.descricao} - {self.fotografo.nome}"




class EnsaioFoto(models.Model):
    ensaio = models.ForeignKey(Ensaio, on_delete=models.CASCADE, related_name="fotos")
    fotografo = models.ForeignKey(Fotografo, on_delete=models.CASCADE, related_name="fotos_ensaios")
    foto = models.BinaryField() 
    escolhida = models.BooleanField(default=False)

    def __str__(self):
        return f"Foto {self.id} do Ensaio {self.ensaio.descricao} - Escolhida: {self.escolhida}"