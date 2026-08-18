from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User

class RegisterForm(UserCreationForm):
    first_name= forms.CharField(max_length=20,required=True,label='Ім\'я',
        widget=forms.TextInput(attrs={'placeholder':"Ваше ім'я",'class':'form-input'})),
    last_name = forms.CharField(max_length=20,required=True,label='Прізвище',
        widget=forms.TextInput(attrs={'placeholder':"Ваше прізвище",'class':'form-input'}))
    email = forms.EmailField(required=True,label='Email',
        widget=forms.EmailInput(attrs={'placeholder':'your@gmail.com','class':'form-input'}))
    username = forms.CharField(label='Логін',
        widget=forms.TextInput(attrs={'placeholder':'Оберіть логін','class':'form-input'}))
    password1 =forms.CharField(label='Пароль',
        widget=forms.PasswordInput(attrs={'placeholder':'Мінімум 8 символів','class':'form-input'})) 
    password2 = forms.CharField(label='Підтвердження паролю',
        widget=forms.PasswordInput(attrs={'placeholder':'Повторіть пароль','class':'form-input'}))
    class Meta:
        model = User
        fields=('first_name',"last_name",'email','username','password1','password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Цей email вже використовується')
        return email
class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Логін',
        widget=forms.TextInput(attrs={'placeholder':'Ваш логін','class':'form-input'}))
    password = forms.CharField(label='Пароль',
        widget=forms.PasswordInput(attrs={'placeholder':'Ваш пароль','class':'form-input'}))

from django import forms
from django.core.validators import MinValueValidator, RegexValidator

class BookingForm(forms.Form):
    """Форма для бронювання та імітації оплати."""
    
    rooms_count = forms.IntegerField(
        min_value=1,
        initial=1,
        label="Кількість номерів",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    card_number = forms.CharField(max_length=16, validators=[RegexValidator(r'^\d{16}$' , 'Введіть 16 цифр картки без пробілів.')] ,label="Номер картки", widget=forms.TextInput(attrs={'class': 'form-control',  'placeholder': '1234567812345678'}))
    cvv = forms.CharField(max_length=3,validators=[RegexValidator(r'^\d{3}$', 'Введіть 3 цифри CVV.')],label="CVV код",widget=forms.PasswordInput(render_value=False, attrs={'class': 'form-control', 'placeholder': '***'}))
    total_amount = forms.DecimalField(max_digits=10,decimal_places=2,label="Сума до оплати",required=False,widget=forms.NumberInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.initial_amount = kwargs.pop('initial_amount', 0)
        
        super().__init__(*args, **kwargs)
        
        self.fields['total_amount'].initial = self.initial_amount

        if not (self.user and self.user.is_superuser):
            self.fields['total_amount'].widget.attrs['readonly'] = True