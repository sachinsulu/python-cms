from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from package.models import Package, SubPackage
from articles.models import Article
from gallery.models import Gallery , GalleryImage
from location.models import Location
from preferences.models import SitePreferences
from services.models import Service



# Create your views here.
def home(request):
    featured_rooms = SubPackage.objects.filter(is_active=True, package__package_type='room').order_by('position')[:4]
    articles = Article.objects.filter(active=True, homepage=True, slug='hotel-rudra').first()
    amenities = Service.objects.filter(status=True, type='service').order_by('position')[:8]
    main_services = Service.objects.filter(status=True, type='main-service').order_by('position')[:4]
    return render(request, 'hotelrudra/index.html', {'featured_rooms': featured_rooms, 'article': articles, 'amenities': amenities})

def about(request, slug):
    article = Article.objects.filter(active=True, slug=slug).first()
    return render(request, 'hotelrudra/about.html', {'article': article})

def rooms(request):
    all_rooms = SubPackage.objects.filter(is_active=True, package__package_type='room').order_by('position')
    return render(request, 'hotelrudra/rooms.html', {'all_rooms': all_rooms})

def amenities(request):
    amenities = Service.objects.filter(status=True, type='service').order_by('position')
    return render(request, 'hotelrudra/amenities.html', {'amenities': amenities})

def gallery(request):
    gallery = Gallery.objects.filter(active=True, type='Innerpage').order_by('position')
    gallery_images = GalleryImage.objects.filter(active=True).order_by('?')
    return render(request, 'hotelrudra/gallery.html', {'gallery': gallery, 'gallery_images': gallery_images})

def contact(request):

    site_location = Location.objects.get_solo()
    site_prefs = SitePreferences.objects.get_solo()

    phones = [p.strip() for p in site_location.phone.split(',')]
    tel = [p.strip() for p in site_location.landline.split(',')]

    if request.method == 'POST':
        name = request.POST.get('fullname')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        message = request.POST.get('message')
        
        # Send email
        try:
            send_mail(
                'New Contact Form Submission',
                f'Name: {name}\nEmail: {email}\nPhone: {phone}\nAddress: {address}\nMessage: {message}',
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],  # Admin email address to receive contacts
                fail_silently=False,
            )
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'Thank you! Your message has been sent.'})
        except Exception as e:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Failed to send email. Please try again later.'})
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
             return JsonResponse({'status': 'success', 'message': 'Form processed.'})

        return redirect('contact')
    return render(request, 'hotelrudra/contact.html', {'site_location': site_location, 'site_prefs': site_prefs, 'phones': phones, 'tel': tel})


def spa(request):
    return render(request, 'hotelrudra/spa.html')