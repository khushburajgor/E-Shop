from django.shortcuts import render , redirect , HttpResponseRedirect

from django.contrib.auth.hashers import  check_password
from store.models.customer import Customer
from django.views import  View

from django.contrib.auth.hashers import make_password


class Login(View):
    return_url = None
    def get(self , request):
        Login.return_url = request.GET.get('return_url')
        return render(request , 'login.html')

    def post(self , request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        customer = Customer.get_customer_by_email(email)
        error_message = None
        if customer:
            flag = check_password(password, customer.password)
            if flag:
                request.session['customer'] = customer.id

                if Login.return_url:
                    return HttpResponseRedirect(Login.return_url)
                else:
                    Login.return_url = None
                    return redirect('homepage')
            else:
                error_message = 'Email or Password invalid !!'
        else:
            error_message = 'Email or Password invalid !!'

        print(email, password)
        return render(request, 'login.html', {'error': error_message})

def logout(request):
    request.session.clear()
    return redirect('login')

def forgot(request):
    if request.method == 'GET':
        return render(request, 'forgot.html')
    else:
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        customer = Customer.get_customer_by_email(email)
        if customer:
            if phone == customer.phone:
                new_pass = email.split('@')[0] + phone[-4:]
                customer.password = make_password(new_pass)
                customer.save()
                return render(request, 'forgot.html', {'success': 'Your new password is: ' + new_pass})
            else:
                return render(request, 'forgot.html', {'error': 'Sorry we can\'t validate you'})
        else:
            return render(request, 'forgot.html',{'error': "User with this email doesn't exist"})

def change(request):
    customer = request.session.get('customer')
    if Customer.objects.filter(id=customer).exists() == False:
        return redirect('/login')
    else:
        customer_obj = Customer.objects.get( id=customer )

    if request.method == 'GET':
        return render(request, 'change.html')
    else:   #POST
        new_pass= request.POST.get('new_pass')
        new_pass2 = request.POST.get('new_pass2')
        if new_pass != new_pass2:
            return render(request,'change.html', {'error': 'The passwords doesn\'t match' })
        customer_obj.password = make_password(new_pass)
        customer_obj.save()
        return redirect('/')
