from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ScanForm
from .utils import analyze_image

@login_required
def upload_scan(request):
    if request.method == 'POST':
        form = ScanForm(request.POST, request.FILES)
        if form.is_valid():
            new_scan = form.save(commit=False)
            new_scan.patient = request.user
            new_scan.save()
            try:
                results = analyze_image(new_scan.image.path, scan_type=new_scan.scan_type)
                return render(request, 'results.html', {
                    'results': results,
                    'image_url': new_scan.image.url,
                    'scan_type': new_scan.get_scan_type_display(),
                    'scan': new_scan
                })
            except Exception as e:
                messages.error(request, f"Error processing image: {str(e)}")
    else:
        form = ScanForm()
    return render(request, 'upload.html', {'form': form})
