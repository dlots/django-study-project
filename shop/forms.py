from django import forms


class AddToCartForm(forms.Form):
    quantity = forms.IntegerField()


class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=64)
    password = forms.CharField(label='Password', max_length=128, widget=forms.PasswordInput)


class RegistrationForm(forms.Form):
    username = forms.CharField(label='Username', max_length=64)
    email = forms.EmailField(label='E-Mail', max_length=128)
    password = forms.CharField(label='Password', min_length=3, max_length=128, widget=forms.PasswordInput)
    password_again = forms.CharField(label='Password, again', min_length=3, max_length=128, widget=forms.PasswordInput)


class CheckoutForm(forms.Form):
    order_address = forms.CharField(label='Delivery address', max_length=500)
    contact_phone = forms.CharField(label='Contact phone number', max_length=13)
