from django.shortcuts import render, get_object_or_404
from package.models import SubPackage
from articles.models import Article
from gallery.models import Gallery , GalleryImage
from location.models import Location
from preferences.models import SitePreferences


# Create your views here.
def home(request):
    featured_rooms = SubPackage.objects.filter(is_active=True).order_by('position')[:4]
    articles = Article.objects.filter(active=True, homepage=True, slug='hotel-rudra').first()
    return render(request, 'hotelrudra/index.html', {'featured_rooms': featured_rooms, 'article': articles})

def about(request):
    article = Article.objects.filter(active=True, slug='about-us').first()
    return render(request, 'hotelrudra/about.html', {'article': article})

def rooms(request):
    all_rooms = SubPackage.objects.filter(is_active=True).order_by('position')
    return render(request, 'hotelrudra/rooms.html', {'all_rooms': all_rooms})

def room_details(request, slug):
    room = get_object_or_404(SubPackage, slug=slug, is_active=True)
    return render(request, 'hotelrudra/room-details.html', {'room': room})

def hall(request):
    return render(request, 'hotelrudra/hall.html')

def restaurant(request):
    return render(request, 'hotelrudra/restaurant.html')

def amenities(request):
    return render(request, 'hotelrudra/amenities.html')

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
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Send email
        send_mail(
            'New Contact Form Submission',
            f'Name: {name}\nEmail: {email}\nMessage: {message}',
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
        
        return redirect('contact')
    return render(request, 'hotelrudra/contact.html', {'site_location': site_location, 'site_prefs': site_prefs, 'phones': phones, 'tel': tel})

def nearby(request):
    return render(request, 'hotelrudra/nearby.html')

def spa(request):
    return render(request, 'hotelrudra/spa.html')