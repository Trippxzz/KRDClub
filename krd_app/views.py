from django.shortcuts import render
from django import forms 
from django.contrib.auth.forms import UserCreationForm ##Para la creacion de usuarios, se usará para completar datos al momento de comprar
# Create your views here.


class ProductoForm(forms.ModelForm):
    class Meta:
        model = ModelProd
        exclude = ("idproducto", "idvehiculo", "stock")