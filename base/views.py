from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm, MessageForm

#Create views here

def login_page(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist!')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'name or password does not exist')
    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logout_user(request):
    logout(request)
    return redirect( 'home')

def register_page(request):
    page = 'register'
    form = UserCreationForm
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid:
            user = form.save(commit=False)
            user.username = user.username.lower()
            login(request, user)
            return redirect('home')
    else:
        messages.error(request, 'An error has occured during registration')


    context = {'page': page, 'form': form}
    return render(request, 'base/login_register.html', context)
    

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | 
        Q(name__icontains=q) | 
        Q(description__icontains=q)
    )
    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))



    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    messages = Message.objects.filter(room=room).order_by('-created')    # room.message_set.all()
    participants = list(room.participants.all())

    if request.method == "POST":
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')   # name='body' in the <input/> obj room.html 
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    context = {'room': room, 'messages': messages, 'participants': participants}
    return render(request, 'base/room.html', context)

def user_profile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    topics = [room.topic for room in rooms]
    room_messages = user.message_set.all()

    context = {'user': user, 'rooms': rooms, 'topics': topics, 'room_messages': room_messages}
    return render(request, "base/profile.html", context)

# CRUD (CREATE READ UPDATE DELETE)
@login_required(login_url='login')
def create_room(request):
    form = RoomForm()

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid(): # - makes sure data is valid for db
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def update_room(request, pk):
    room = Room.objects.get(id=pk)  
    form = RoomForm(instance=room)  # Just fills all the forms at ./update-room/pk/ url

    if request.user != room.host:
        return HttpResponse('Not enough permission')

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)    # intance=room to specify what room is to be updated
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('Not enough permission')
    if request.method == 'POST':    
        room.delete()
        return redirect('home')
    context = {'obj': room}
    return render(request, 'base/delete.html', context)
# CRUD end

# CRUD chat room messages

@login_required(login_url='login')
def update_message(request, pk):
    ...

@login_required(login_url='login')
def delete_message(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse('Not enough permission')
    if request.method == 'POST':    
        message.delete()
        return redirect('home')
    context = {'obj': message}
    return render(request, 'base/delete.html', context)