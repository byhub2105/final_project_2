from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout
from .models import RoomType, CheckInSession, Booking , Score
from .forms import BookingForm,LoginForm,RegisterForm
import json
from django.http import JsonResponse
def home(request):
    return render(request, 'booking/home.html')
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            messages.success(request,f'Вітаємо,{user.first_name}!')
            return redirect('home')
        messages.error(request,'Будь ласка переробіть форму')
    else:
        form = RegisterForm()
    return render(request,'booking/register.html',{'form':form})
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request,data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request,user)
            messages.success(request,f'З поверненням, {user.first_name or user.last_name}')
            return redirect(request.GET.get('next','home'))
        messages.error(request,'Невірний логін або пароль')
    else:
        form = LoginForm()
    return render(request,'booking/login.html',{'form':form})
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request,'Ви успішно вийшли')
    return redirect('home')
def room_type_list(request):
    room_types = RoomType.objects.all()
    return render(request, 'booking/room_type_list.html', {'room_types': room_types})

def room_type_detail(request, pk):
    room = get_object_or_404(RoomType, pk=pk)
    sessions = room.checkinsessions.filter(available_spots__gt=0).order_by('date', 'start_time')
    return render(request, 'booking/room_type_detail.html', {
        'room_type': room, 
        'sessions': sessions
    })

@login_required
def book_session(request, pk):
    session = CheckInSession.objects.get(pk=pk)
    base_price = session.room.price
    if request.method == 'POST':
        form = BookingForm(request.POST, user=request.user, initial_amount=base_price)
        if form.is_valid():
            rooms_requested = form.cleaned_data['rooms_count']
            final_price = base_price * rooms_requested
            Booking.objects.create(
                user=request.user,
                session=session,
                total_price=final_price,
                quantity=rooms_requested
            )
            session.available_spots -= rooms_requested
            session.save()
            return redirect('profile')  
    else:
        form = BookingForm(user=request.user, initial_amount=base_price)

    return render(request, 'booking/book_session.html', {
        'form': form,
        'session': session
    })

@login_required
def booking_confirmation(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    return render(request, 'booking/confirmation.html', {'booking': booking})

@login_required
def profile_view(request):
    all_bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    active_bookings = []
    past_bookings = []
    for booking in all_bookings:
        if booking.session.is_past:
            past_bookings.append(booking)
        else:
            active_bookings.append(booking)
            
    return render(request, 'booking/profile.html', {
        'active_bookings': active_bookings,
        'past_bookings': past_bookings,
    })
def game_view(request):
    return render(request, 'booking/minigame.html')
def save_score_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            player_name = data.get('player_name', 'Анонім')
            game_name = data.get('game_name', 'Змійка')
            score = data.get('score', 0)
            Score.objects.create(
                player_name=player_name,
                game_name=game_name,
                score=score
            )
            return JsonResponse({'status': 'success', 'message': 'Результат збережено!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'Дозволено лише POST-запити'}, status=405)
def leaderboard_view(request):
    top_scores = Score.objects.filter(game_name='Змійка').order_by('-score')[:10]
    return render(request, 'booking/leaderboard.html', {'scores': top_scores})