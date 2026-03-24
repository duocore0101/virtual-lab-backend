from django.shortcuts import render

def pricing_view(request):
    return render(request, "public/pricing.html")


def about(request):
    return render(request, 'public/about.html')


def gallery_view(request):
    return render(request, "public/gallery.html")