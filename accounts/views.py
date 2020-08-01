from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import *
from .forms import *
from django.forms import inlineformset_factory
# Create your views here.
from .filters import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate,logout,login
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user,allowed_users,admin_only
from django.contrib.auth.models import Group

@unauthenticated_user
def register(request):
    form = createuserform()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            group = Group.objects.get(name='customer')
            user.groups.add(group)
            
            Customer.objects.create(user=user)
            messages.success(request,'account was created for ' + form.cleaned_data.get('username'))
            return redirect('login')
    
    
    
    context = {
        'form' : form
    }
    return render(request,'accounts/register.html',context)

@unauthenticated_user
def loginpage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password  = request.POST.get('password')
        user = authenticate(request,username=username,password=password)

        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.info(request,'username or password is incorrect')    

    context = {}
    return render(request,'accounts/login.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userpage(request):
    orders = request.user.customer.order_set.all()
    total_orders = orders.count()
    orders_delivered = orders.filter(status='Delivered').count() 
    orders_pending = orders.filter(status='Pending').count()
    context={
        'orders' : orders,
        'total_orders' : total_orders,
        'orders_pending' : orders_pending,
        'orders_delivered' : orders_delivered,
    }
    return render(request,'accounts/user.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def accountsettings(request):
    customer = request.user.customer
    form = customerform(instance=customer)

    if request.method == 'POST':
        form = customerform(request.POST,request.FILES,instance=customer)
        if form.is_valid():
            form.save()


    context = {
        'form' : form
    }
    return render(request,'accounts/account_settings.html',context)


def logoutuser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
@admin_only
def home(request):
    customers = Customer.objects.all()
    orders = Order.objects.all()
    total_orders = orders.count()
    orders_delivered = Order.objects.filter(status='Delivered').count()
    orders_pending = Order.objects.filter(status='Pending').count()
    mydict = {
        'customers' : customers,
        'orders'  : orders,
        'total_orders' : total_orders,
        'orders_pending' : orders_pending,
        'orders_delivered' : orders_delivered,
    }

    return render(request,'accounts/dashboard.html',context=mydict)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    products = Product.objects.all()
    mydict = {
        'products' : products
    }
    return render(request,'accounts/products.html',context=mydict)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request,pk_test):
    customer = Customer.objects.get(id=pk_test)
    order = customer.order_set.all()
    order_count = order.count()

    myfilter = orderfilter(request.GET,queryset=order)
    order = myfilter.qs


    mydict = {
        'customer' : customer,
        'orders' : order,
        'order_count' : order_count,
        'myfilter' : myfilter,
    }
    return render(request,'accounts/customer.html',context=mydict)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def create_order(request,pk):
    orderformset = inlineformset_factory(Customer,Order,fields=('product','status'),extra=4)
    customer = Customer.objects.get(id=pk)
    formset = orderformset(queryset=Order.objects.none(),instance=customer)
    if request.method == 'POST':
        formset = orderformset(request.POST,instance=customer)
        if formset.is_valid(): 
            formset.save()
            return redirect('customer',pk)
    
    
    mydict = {
        'customer' : customer,
        'formset' : formset,
    }
    return render(request,'accounts/order_form.html',context=mydict)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def update_order(request,pk):
    order = Order.objects.get(id=pk)
    form = orderform(instance=order)
    if request.method == 'POST':
        form = orderform(request.POST,instance=order)
        if form.is_valid():
            form.save()  
            return redirect('/')

    mydict = {
        'form' : form
    }
    return render(request,'accounts/order_form.html',context=mydict)        

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def delete_order(request,pk):
    order = Order.objects.get(id=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('/')
    mydict ={
        'order' : order
    }
    return render(request,'accounts/delete.html',context=mydict)            