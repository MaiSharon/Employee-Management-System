from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth import authenticate
import random
import hashlib

# Simulate sending SMS
def send_sms(code, phone_number):
    print(f'Sending SMS code {code} to {phone_number}')

# Generate secure random token
def generate_token():
    return hashlib.sha256(str(random.randint(10000, 99999)).encode()).hexdigest()

def register_popup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        sms_code = request.POST['sms_code']

        # Validate SMS code from session
        if sms_code == request.session.get('sms_code'):
            user = User.objects.create_user(username=username, password=password)
            user.save()

            # Generate token for future secure operations
            token = generate_token()
            request.session['token'] = token
            return JsonResponse({'status': 'success', 'token': token})
        else:
            return JsonResponse({'status': 'fail', 'reason': 'Invalid SMS code'})

    # Generate random SMS code and save it in session
    sms_code = random.randint(100000, 999999)
    request.session['sms_code'] = sms_code

    # Send SMS
    send_sms(sms_code, 'your_phone_number_here')

    return render(request, 'login_register.html')
