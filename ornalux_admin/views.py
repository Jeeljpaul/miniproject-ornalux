from django.shortcuts import render
from django.http import JsonResponse
from .forms import ProductForm, ProductImageForm
from .models import ProductImage

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        image_form = ProductImageForm(request.POST, request.FILES)
        
        if form.is_valid() and image_form.is_valid():
            product = form.save()
            
            # Save multiple images
            for image in request.FILES.getlist('images'):
                ProductImage.objects.create(product=product, image=image)

            return JsonResponse({'success': True, 'message': 'Product and images added successfully!'})
        else:
            return JsonResponse({'success': False, 'message': 'There was an error with the form submission.'})
    else:
        form = ProductForm()
        image_form = ProductImageForm()

    return render(request, 'add_product.html', {'form': form, 'image_form': image_form})
