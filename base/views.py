from multiprocessing import context
from django.shortcuts import render, redirect
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.forms import  UserCreationForm

# Create your views here.

def loginPg(request):
    page='login'
    if request.user.is_authenticated:
        messages.warning(request,'you are already logged in')
        return redirect('home')

    if request.method == 'POST':
        username=request.POST.get('username')
        password=request.POST.get('password')

        try:
            user=User.objects.get(username=username)
        except:
            messages.error(request,'User Does not exist')
        
        user=authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)   #creates a session in database and browser of that user
            return redirect('home')
        else:
            messages.error(request,'Username or password is invalid')

        
    context={'page': page}
    return render(request,'base/login_registration.html',context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def register(request):
    form=UserCreationForm()

    if request.method == 'POST':
        form=UserCreationForm(request.POST)
        if form.is_valid():
            user=form.save(commit=False)
            user.username=user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
             messages.error(request,'there is a error while registration')

    context={'form': form}
    return render(request,'base/login_registration.html',context)

def home(request):
    q=request.GET.get('q')
    print(request)
    if q==None:
        q=''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q)|
        Q(name__icontains=q)|
        Q(description__icontains=q)
        )
    room_count=rooms.count()
    topics= Topic.objects.all()
    room_message=Message.objects.filter(Q(room__topic__name__icontains=q)).order_by('-updated','-created')[:10]
    return render(request, 'base/home.html',{'rooms': rooms, 'topics': topics,'room_count': room_count, 'room_message': room_message})


def room(request,pk):
    room = Room.objects.get(id = pk)
    room_messages = room.message_set.all()
    participants=room.participants.all()
    if request.method == 'POST':
        message=Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        return redirect('room', pk=room.id)
        

    return render(request, 'base/room.html', {'room': room,'room_messages': room_messages, 'participants': participants})

def userProfile(request,pk):
    q=request.GET.get('q')
    if q==None:
        q=''
    user=User.objects.get(id=pk)
    topics= Topic.objects.all()
    rooms=user.room_set.filter(
        Q(topic__name__icontains=q)|
        Q(name__icontains=q)|
        Q(description__icontains=q)
        )
    room_count=rooms.count()
    room_message=user.message_set.filter(Q(room__topic__name__icontains=q)).order_by('-updated','-created')[:10]
    context={'topics': topics, 'user':user, 'rooms': rooms,'room_count': room_count, 'room_message': room_message}
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def createRoom(request):
    form=RoomForm()
    topics=Topic.objects.all()
    if request.method == 'POST':
        topic_name=request.POST.get('topic')
        topic, created=Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )
        # form=RoomForm(request.POST)
        # if form.is_valid():
        #     room=form.save(commit=False)
        #     room.host=request.user
        #     room.save()
        return redirect('home')
    return render(request,'base/room-form.html',{'form': form,'topics': topics})

@login_required(login_url='login')
def updateRoom(request,pk):
    room =Room.objects.get(id=pk)
    form=RoomForm(instance=room)
    topics=Topic.objects.all()
    if request.user!=room.host:
        return HttpResponse('You are not a valid user to edit this room')
    if request.method == 'POST':
        form=RoomForm(request.POST,instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    return render(request, 'base/room-form.html', {'form': form,'topics': topics,'room':room})

@login_required(login_url='login')
def deleteRoom(request,pk):
    room=Room.objects.get(id=pk)

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj': room})

@login_required(login_url='login')
def deleteMessage(request,pk):
    message=Message.objects.get(id=pk)

    if request.user!= message.user:
        return HttpResponse('You cannot delete this message')
    if request.method == 'POST':
        room=message.room
        message.delete()
        return redirect('room', room.id)
    return render(request,'base/delete.html',{'obj': message})

@login_required(login_url='login')
def updateUser(request):
    form=UserForm(instance=request.user)

    if request.method == 'POST':
        form = UserForm(request.POST,instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request,'successfully updated the profile')
            return redirect('user-profile', pk=request.user.id)
    return render(request,'base/update-user.html',{'form': form})