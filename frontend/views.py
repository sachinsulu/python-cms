from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'hotelrudra/index.html')

def about(request):
    return render(request, 'hotelrudra/about.html')

def rooms(request):
    return render(request, 'hotelrudra/rooms.html')

def room_details(request):
    return render(request, 'hotelrudra/room-details.html')

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