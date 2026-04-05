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
from testimonials.models import Testimonial 
from slideshow.models import Slideshow
import requests



# Create your views here.
def home(request):
    featured_rooms = SubPackage.objects.filter(is_active=True, package__package_type='room').order_by('position')[:4]
    articles = Article.objects.filter(active=True, homepage=True, slug='hotel-rudra').first()
    amenities = Service.objects.filter(status=True, type='service').order_by('position')[:8]
    main_services = Service.objects.filter(status=True, type='main-service').order_by('position')[:4]
    testimonials = Testimonial.objects.filter(active=True).order_by('position')[:4]
    gallery = Gallery.objects.filter(active=True, type='Homepage').order_by('position')[:8]
    gallery_images = GalleryImage.objects.filter(active=True, gallery__type='Homepage').order_by('?')
    if Slideshow.objects.filter(active=True, type='video').exists():
        slideshow = Slideshow.objects.filter(active=True, type='video').order_by('position')
    else:
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
    gallery_images = GalleryImage.objects.filter(active=True, gallery__type='Innerpage').order_by('position')
    return render(request, 'hotelrudra/gallery.html', {'gallery': gallery, 'gallery_images': gallery_images})

def send_enquiry_email(data):
    """Helper function to send enquiry/contact emails"""
    name = data.get('fullname')
    email = data.get('email')
    phone = data.get('phone')
    address = data.get('address')
    message = data.get('message')
    subject = data.get('subject', 'New Contact Form Submission')
    event_date = data.get('form_eventDate')
    pax = data.get('form_pax')
    recaptcha_response = data.get('g-recaptcha-response')

    # Verify reCAPTCHA
    if not recaptcha_response:
        return False, "Please complete the reCAPTCHA."
    
    verify_url = "https://www.google.com/recaptcha/api/siteverify"
    payload = {
        'secret': settings.RECAPTCHA_SECRET_KEY,
        'response': recaptcha_response
    }
    try:
        response = requests.post(verify_url, data=payload)
        result = response.json()
        if not result.get('success'):
            return False, "reCAPTCHA verification failed. Please try again."
    except Exception as e:
        print(f"reCAPTCHA Error: {e}")
        return False, "Could not verify reCAPTCHA. Please try again later."
    
    # Construct email body
    body = f'Name: {name}\nEmail: {email}\nPhone: {phone}\nAddress: {address}\n'
    if event_date:
        body += f'Event Date: {event_date}\n'
    if pax:
        body += f'Number of Guests: {pax}\n'
    body += f'\nMessage:\n{message}'

    # Get recipient email dynamically from Location settings
    location = Location.objects.get_solo()
    recipient_email = location.email_address or settings.DEFAULT_FROM_EMAIL

    try:
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
        )
        return True, "Thank you! Your enquiry has been sent."
    except Exception as e:
        print(f"Mail Error: {e}") 
        return False, "Failed to send enquiry. Please try again later."

def enquiry(request):
    """Dedicated view for AJAX-based enquiries from modals"""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        success, message = send_enquiry_email(request.POST)
        if success:
            return JsonResponse({'status': 'success', 'message': message})
        else:
            return JsonResponse({'status': 'error', 'message': message})
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)

def contact(request):
    site_location = Location.objects.get_solo()
    site_prefs = SitePreferences.objects.get_solo()

    from core.phone_utils import split_and_normalize_phones
    phones = split_and_normalize_phones(site_location.phone)
    tel = split_and_normalize_phones(site_location.landline)

    if request.method == 'POST':
        success, message = send_enquiry_email(request.POST)
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if success:
                return JsonResponse({'status': 'success', 'message': message})
            else:
                return JsonResponse({'status': 'error', 'message': message})
        
        if success:
             from django.contrib import messages
             messages.success(request, message)
        else:
             from django.contrib import messages
             messages.error(request, message)

        return redirect('contact')
    return render(request, 'hotelrudra/contact.html', {'site_location': site_location, 'site_prefs': site_prefs, 'phones': phones, 'tel': tel})

def Main_Service(request):
    main_services = Service.objects.filter(status=True, type='main-service').order_by('position')
    return render(request, 'hotelrudra/spa.html', {'main_services': main_services})

def service_detail(request, slug):
    services = Service.objects.filter(status=True)
    service = next((s for s in services if s.slug == slug), None)
    if not service:
        from django.http import Http404
        raise Http404("Service not found")
    return render(request, 'hotelrudra/service-detail.html', {'service': service})