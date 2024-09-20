from django.shortcuts import render
from django.http import JsonResponse
from .forms import ProductForm

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Product added successfully!'})
        else:
            return JsonResponse({'success': False, 'message': 'There was an error with the form submission.'})
    else:
        form = ProductForm()

    return render(request, 'add_product.html', {'form': form})
