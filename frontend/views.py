from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse, Http404
from django.utils.text import slugify
from package.models import Package, SubPackage
from articles.models import Article
from gallery.models import Gallery , GalleryImage
from location.models import Location
from preferences.models import SitePreferences
from services.models import Service
from testimonials.models import Testimonial 
from slideshow.models import Slideshow



# Create your views here.
def home(request):
    featured_rooms = SubPackage.objects.filter(is_active=True, package__package_type='room').order_by('position')[:4]
    articles = Article.objects.filter(active=True, homepage=True, slug='hotel-rudra').first()
    amenities = Service.objects.filter(status=True, type='service').order_by('position')[:8]
    main_services = Service.objects.filter(status=True, type='main-service').order_by('position')[:4]
    testimonials = Testimonial.objects.filter(active=True).order_by('position')[:4]
    gallery = Gallery.objects.filter(active=True, type='Homepage').order_by('position')[:8]
    gallery_images = GalleryImage.objects.filter(active=True, gallery__type='Homepage').order_by('?')
    slideshow = Slideshow.objects.filter(active=True, type='image').order_by('position')
    return render(request, 'hotelrudra/index.html', {'featured_rooms': featured_rooms, 'article': articles, 'amenities': amenities, 'main_services': main_services, 'testimonials': testimonials, 'gallery': gallery, 'gallery_images': gallery_images, 'slideshow': slideshow})



def rooms(request):
    all_rooms = SubPackage.objects.filter(is_active=True, package__package_type='room').order_by('position')
    return render(request, 'hotelrudra/rooms.html', {'all_rooms': all_rooms})

def amenities(request):
    amenities = Service.objects.filter(status=True, type='service').order_by('position')
    return render(request, 'hotelrudra/amenities.html', {'amenities': amenities})

def gallery(request):
    gallery = Gallery.objects.filter(active=True, type='Innerpage').order_by('position')
    gallery_images = GalleryImage.objects.filter(active=True, gallery__type='Innerpage').order_by('?')
    return render(request, 'hotelrudra/gallery.html', {'gallery': gallery, 'gallery_images': gallery_images})

def contact(request):

    site_location = Location.objects.get_solo()
    site_prefs = SitePreferences.objects.get_solo()

    phones = [p.strip() for p in site_location.phone.split(',') if p.strip()]
    tel = [p.strip() for p in site_location.landline.split(',') if p.strip()]

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

def Main_Service(request):
    main_services = Service.objects.filter(status=True, type='main-service').order_by('position')
    return render(request, 'hotelrudra/spa.html', {'main_services': main_services})

def service_detail(request, slug):
    service = next(
        (s for s in Service.objects.filter(status=True) if s.slug == slug),
        None
    )
    if not service:
        raise Http404("Service not found")
    return render(request, 'hotelrudra/service-detail.html', {'service': service})