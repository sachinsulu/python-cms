from django.shortcuts import render, get_object_or_404
from package.models import SubPackage

# Create your views here.
def home(request):
    featured_rooms = SubPackage.objects.filter(is_active=True).order_by('position')[:4]
    return render(request, 'hotelrudra/index.html', {'featured_rooms': featured_rooms})

def about(request):
    return render(request, 'hotelrudra/about.html')

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
    return render(request, 'hotelrudra/gallery.html')

def contact(request):
    return render(request, 'hotelrudra/contact.html')

def nearby(request):
    return render(request, 'hotelrudra/nearby.html')

def spa(request):
    return render(request, 'hotelrudra/spa.html')