from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator
from django.conf import settings
from django.utils import timezone
class RoomType(models.Model):
    title = models.CharField(max_length=100, verbose_name='Назва')
    description = models.TextField(verbose_name='Опис',blank=True)
    rooms = models.PositiveIntegerField(default=1,verbose_name='Кількість кімнат у номері')
    total_inventory = models.PositiveIntegerField(validators=[MinValueValidator(1)],verbose_name="Загальна кількість таких номерів у готелі")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Базова ціна")
    amenities = models.JSONField(default=list, blank=True, verbose_name="Зручності (Wi-Fi, кондиціонер тощо)")

    class Meta:
        verbose_name = "Тип номеру"
        verbose_name_plural = "Типи номерів"
    def __str__(self):
        return f'{self.title}'

class CheckInSession(models.Model):
    room = models.ForeignKey(RoomType, on_delete=models.CASCADE,related_name='checkinsessions',verbose_name='Кімната у готелі')
    date = models.DateField(verbose_name='Дата заїзду')
    start_time = models.TimeField(verbose_name="Час заїзду (Check-in)")
    check_out = models.DateTimeField(verbose_name="Дата та час виїзду", null=True, blank=True)
    available_spots = models.PositiveIntegerField(verbose_name="Доступно вільних номерів")
    @property
    def is_past(self):
        if self.check_out:
            return timezone.now() > self.check_out
        return False
    class Meta:
        verbose_name = "Сеанс заїзду"
        verbose_name_plural = "Сеанси заїзду"
        ordering = ['date', 'start_time']
    @property
    def is_fully_booked(self) -> bool:
        return self.available_spots == 0

    def save(self, *args, **kwargs):
        if not self.pk and self.available_spots is None:
            self.available_spots = self.room.total_inventory
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.room} | {self.date} ({self.start_time} - {self.check_out}) | Вільних: {self.available_spots}"

class Booking(models.Model):
    
    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'Очікує оплати'
        PAID = 'paid', 'Оплачено'
        CANCELLED = 'cancelled', 'Скасовано'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="bookings",
        verbose_name="Клієнт"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Кількість номерів")
    session = models.ForeignKey(
        CheckInSession, 
        on_delete=models.PROTECT, 
        related_name="bookings",
        verbose_name="Сеанс заїзду"
    )
    booking_date = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Дата та час бронювання"
    )
    status = models.CharField(
        max_length=20, 
        choices=StatusChoices.choices, 
        default=StatusChoices.PENDING,
        verbose_name="Статус"
    )
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Загальна вартість"
    )
    
    class Meta:
        verbose_name = "Бронювання"
        verbose_name_plural = "Бронювання"

    def __str__(self):
        return f"Бронювання #{self.id} — {self.user} {self.quantity} ({self.get_status_display()})"
class Score(models.Model):
    player_name = models.CharField(max_length=50, verbose_name="Ім'я гравця")
    game_name = models.CharField(max_length=50, verbose_name="Назва гри")
    score = models.IntegerField(verbose_name="Результат")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Час створення")

    class Meta:
        ordering = ['-score']

    def __str__(self):
        return f"{self.player_name} - {self.game_name}: {self.score}"