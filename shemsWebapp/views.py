from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import connection
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import (
    Customer,
    Location,
    Device
)
from .forms import (
    CustomerForm,
    LocationForm,
    DeviceForm
)

def dictfetchall(cursor):
    """
    Return all rows from a cursor as a dict.
    Assume the column names are unique.
    """
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_customer_locations(customer):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Location JOIN CustomerLocation ON Location.lid =  CustomerLocation.lid_id where CustomerLocation.cid_id = %s;", [customer.cid])
        customer_locations = dictfetchall(cursor)
    return customer_locations

def get_customer_devices(customer):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Device JOIN CustomerLocation ON Device.lid_id =  CustomerLocation.lid_id where CustomerLocation.cid_id = %s;", [customer.cid])
        customer_devices = dictfetchall(cursor)
    return customer_devices

# Create your views here.
@login_required
def profile(request):
    curr_user = request.user

    customer = Customer.objects.get(user=curr_user)
    customer_locations = get_customer_locations(customer)
    customer_devices= get_customer_devices(customer)
    context = {}
    context.update({"cid": customer.cid})
    context.update({"first_name": customer.first_name})
    context.update({"last_name": customer.last_name})
    context.update({"billing_address": customer.billing_address})

    return render(request, "profile.html", context)

@login_required
def locations(request):
    curr_user = request.user
    
    customer = Customer.objects.get(user=curr_user)
    customer_locations = get_customer_locations(customer)
    context = {}
    context.update({"customer_locations": customer_locations})

    if request.method == "POST":
        button = request.POST.get("delete_location")
        lid = request.POST.get("lid")
        if button == "delete_location":
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM CustomerLocation WHERE cid_id = %s AND lid_id = %s;", (customer.cid, lid))
            return redirect(reverse("shemsWebapp:locations"))

    return render(request, "service_locations.html", context)

@login_required
def devices(request):
    curr_user = request.user

    customer = Customer.objects.get(user=curr_user)
    customer_devices= get_customer_devices(customer)
    context = {}
    context.update({"customer_devices": customer_devices})

    if request.method == "POST":
        button = request.POST.get("delete_device")
        did = request.POST.get("did")
        if button == "delete_device":
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM Device WHERE did = %s", (did))
            return redirect(reverse("shemsWebapp:devices"))

    return render(request, "devices.html", context)

@login_required
def add_location(request):
    if request.method == "POST":
        form = LocationForm(request.POST)
        if form.is_valid():
            loc = form.save(commit=False)
            curr_user = request.user
            customer = Customer.objects.get(user=curr_user)
            cid = customer.cid
            location = Location.objects.create(num_bedrooms=loc.num_bedrooms, num_occupants=loc.num_occupants, area=loc.area, unit=loc.unit, street=loc.street, building=loc.building, city=loc.city, zipcode=loc.zipcode)
            with connection.cursor() as cursor:
                # cursor.execute("INSERT INTO Location(num_bedrooms, num_occupants, area, unit, street, building, city, zipcode) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (loc.num_bedrooms, loc.num_occupants, loc.area, loc.unit, loc.street, loc.building, loc.city, loc.zipcode))
                cursor.execute("INSERT INTO CustomerLocation(cid_id, lid_id) VALUES (%s, %s)", (cid, location.lid))           
            return redirect(reverse("shemsWebapp:locations"))
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
            return render(request, "add_location.html", {'form': form})
    else:
        form = LocationForm()
        context = {}
        context["form"] = form

        return render(request, "add_location.html", context=context)

@login_required
def add_device(request):
    curr_user = request.user
    customer = Customer.objects.get(user=curr_user)
    with connection.cursor() as cursor:
        cursor.execute("SELECT lid_id FROM CustomerLocation where cid_id = %s;", [customer.cid])
        result_tuples = cursor.fetchall()
        customer_locations = [item[0] for item in result_tuples]
    if request.method == "POST":       
        form = DeviceForm(request.POST, lids=customer_locations)
        if form.is_valid():
            device = form.save(commit=False)
            lid = device.lid.lid
            model_num = device.model_num.model_num
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO Device(lid_id, model_num_id) VALUES (%s, %s)", (lid, model_num))
            return redirect(reverse("shemsWebapp:devices"))
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
            return render(request, "add_device.html", {'form': form})
    else:
        form = DeviceForm(lids=customer_locations)
        context = {}
        context["form"] = form
        if form.is_valid():
            return render(request, "add_device.html", context=context)
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
            return render(request, "add_device.html", context=context)
        
@login_required
def edit_customer(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            user = request.user
            first_name = customer.first_name
            last_name = customer.last_name
            billing_address = customer.billing_address
            user_id = user.pk
            with connection.cursor() as cursor:
                cursor.execute("UPDATE Customer SET first_name = %s, last_name = %s, billing_address = %s where user_id = %s", (first_name, last_name, billing_address, user_id))
            return redirect(reverse("shemsWebapp:profile"))
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
            return render(request, "edit_customer.html", {'form': form})
    else:
        form = CustomerForm()
        context = {}
        context["form"] = form
        return render(request, "edit_customer.html", context=context)

def home(request):
    if request.user.is_authenticated:
        return redirect("shemsWebapp:profile")
    else:
        return redirect("shemsAccount:login")
