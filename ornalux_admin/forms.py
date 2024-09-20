from django import forms
from .models import Product
from django.core.exceptions import ValidationError
import re

class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = [
            'product_name', 'product_description', 'category', 'subcategory', 'price',
            'discount', 'stock_quantity', 'weight', 'material', 'metal_type', 'gemstones',
            'gender', 'occasion', 'sku', 'try_at_home', 'delivery_options', 'return_policy', 'tags', 'images'
        ]
        widgets = {
            'product_description': forms.Textarea(attrs={'rows': 4}),
            'delivery_options': forms.Textarea(attrs={'rows': 2}),
            'return_policy': forms.Textarea(attrs={'rows': 2}),
            'images': forms.ClearableFileInput(attrs={'multiple': True}),
        }

    def clean_product_name(self):
        product_name = self.cleaned_data.get('product_name')
        if re.search(r'\d|[^a-zA-Z\s]', product_name):
            raise ValidationError("Product name cannot contain numbers or special characters.")
        return product_name

    def clean_subcategory(self):
        subcategory = self.cleaned_data.get('subcategory')
        if re.search(r'\d|[^a-zA-Z\s]', subcategory):
            raise ValidationError("Subcategory cannot contain numbers or special characters.")
        return subcategory

    def clean_material(self):
        material = self.cleaned_data.get('material')
        if re.search(r'\d|[^a-zA-Z\s]', material):
            raise ValidationError("Material cannot contain numbers or special characters.")
        return material

    def clean_metal_type(self):
        metal_type = self.cleaned_data.get('metal_type')
        if re.search(r'\d|[^a-zA-Z\s]', metal_type):
            raise ValidationError("Metal type cannot contain numbers or special characters.")
        return metal_type

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise ValidationError("Price must be greater than 0.")
        return price

    def clean_stock_quantity(self):
        stock_quantity = self.cleaned_data.get('stock_quantity')
        if stock_quantity <= 0:
            raise ValidationError("Stock quantity must be a positive number.")
        return stock_quantity

    def clean_weight(self):
        weight = self.cleaned_data.get('weight')
        if weight <= 0:
            raise ValidationError("Weight must be greater than 0 grams.")
        return weight

    def clean_sku(self):
        sku = self.cleaned_data.get('sku')
        if re.search(r'[^a-zA-Z0-9]', sku):
            raise ValidationError("SKU can only contain letters and numbers.")
        return sku
