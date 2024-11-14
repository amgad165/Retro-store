from django import forms
from .models import ProductImage

class ProductImageForm(forms.ModelForm):
    images = forms.ImageField(widget=forms.ClearableFileInput(), required=False)

    class Meta:
        model = ProductImage
        fields = ['images']
