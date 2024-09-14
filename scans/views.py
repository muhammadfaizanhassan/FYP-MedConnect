from django.shortcuts import render
from .forms import ScanForm
from .utils import analyze_image

def upload_scan(request):
    if request.method == 'POST':
        form = ScanForm(request.POST, request.FILES)
        if form.is_valid():
            new_scan = form.save()  # Save the uploaded image to the database
            results = analyze_image(new_scan.image.path)  # Pass the image to the analyzer
            return render(request, 'results.html', {
                'results': results,
                'image_url': new_scan.image.url  # Pass the image URL to the results page
            })
    else:
        form = ScanForm()
    return render(request, 'upload.html', {'form': form})
