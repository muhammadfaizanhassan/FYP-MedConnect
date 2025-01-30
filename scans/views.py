from django.shortcuts import render
from django.contrib import messages
from .forms import ScanForm
from .utils import analyze_image

def upload_scan(request):
    if request.method == 'POST':
        form = ScanForm(request.POST, request.FILES)
        if form.is_valid():
            new_scan = form.save()
            try:
                results = analyze_image(new_scan.image.path)
                return render(request, 'results.html', {
                    'results': results,
                    'image_url': new_scan.image.url
                })
            except Exception as e:
                messages.error(request, f"Error processing image: {str(e)}")
    else:
        form = ScanForm()
    return render(request, 'upload.html', {'form': form})
