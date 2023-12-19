from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import connection
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime
# Create your views here.

monthToName = {1: 'January',
                2: 'February',
                3: 'March',
                4: 'April',
                5: 'May',
                6: 'June',
                7: 'July',
                8: 'August',
                9: 'September',
                10: 'October',
                11: 'November',
                12: 'December'}

from .models import (
    Customer,
    Location,
    Device,
    DeviceModel
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
        cursor.execute(f"SELECT * FROM Location JOIN CustomerLocation ON Location.lid =  CustomerLocation.lid_id where CustomerLocation.cid_id = {customer.cid};")
        customer_locations = dictfetchall(cursor)
    return customer_locations

def get_customer_devices(customer):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM Device JOIN CustomerLocation ON Device.lid_id =  CustomerLocation.lid_id where CustomerLocation.cid_id = {customer.cid};")
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
    
    year = datetime.now().year
    month = datetime.now().month
    energyPriceGraphObject = getEnergyPrice(customer.cid, year, month)
    totalEnergyUsageObject = getTotalEnergyUsageByLocation(customer.cid, year, month)
    
    locationEnergyPieObject = getDeviceTypeEnergyUsage(customer.cid, year, month)
    deviceDailyEnergyUsageObject = getDeviceDailyEnergyUsage(customer.cid)                                    
    context.update({'total_energy_usage': totalEnergyUsageObject})
    context.update({'energy_price': energyPriceGraphObject})
    context.update({'location_energy_pie': locationEnergyPieObject})
    context.update({'device_energy_use': deviceDailyEnergyUsageObject})
    context.update({'month': monthToName[month]})
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
                cursor.execute(f"DELETE FROM CustomerLocation WHERE cid_id = {customer.cid} AND lid_id = {lid};")
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
                cursor.execute(f"DELETE FROM Device WHERE did = {did}")
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
            # location = Location.objects.create(num_bedrooms=loc.num_bedrooms, num_occupants=loc.num_occupants, area=loc.area, unit=loc.unit, street=loc.street, building=loc.building, city=loc.city, zipcode=loc.zipcode)
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO Location(num_bedrooms, num_occupants, area, "
                               + f"unit, street, building, city, zipcode) VALUES ({loc.num_bedrooms}," 
                               + f"{loc.num_occupants}, {loc.area}, {loc.unit}, {loc.street}, "
                               + f"{loc.building}, {loc.city}, {loc.zipcode}) returning lid")
                lid = cursor.fetchone()[0]                    
                cursor.execute(f"INSERT INTO CustomerLocation(cid_id, lid_id) VALUES ({cid}, {lid})")           
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

def load_device_types(request):
    model_type = request.GET.get('model_type')
    if model_type == "All":
        models = DeviceModel.objects.all()
    else:
        models = DeviceModel.objects.filter(model_type=model_type)
    return render(request, 'device_types_options.html', {'models': models})

@login_required
def add_device(request):
    curr_user = request.user
    customer = Customer.objects.get(user=curr_user)
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT lid_id FROM CustomerLocation where cid_id = {customer.cid};")
        result_tuples = cursor.fetchall()
        customer_locations = [item[0] for item in result_tuples]
    if request.method == "POST":       
        form = DeviceForm(request.POST, lids=customer_locations)
        if form.is_valid():
            device = form.save(commit=False)
            lid = device.lid.lid
            model_num = device.model_num.model_num
            with connection.cursor() as cursor:
                cursor.execute(f"INSERT INTO Device(lid_id, model_num_id) VALUES ({lid},{model_num})")
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
                cursor.execute(f"UPDATE Customer SET first_name = {first_name}, last_name = {last_name}, " 
                                + f"billing_address = {billing_address} where user_id = {user_id}")
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


'''
Gets the daily energy usage of a particular device for a period of time
'''
def getDeviceDailyEnergyUsage(cid):

    with connection.cursor() as cursor:
        #device energy consumption by day 
        cursor.execute(f"SELECT DATE_TRUNC('DAY', timestamp) as time, device.did, SUM(value)"
                       + " FROM (customerLocation JOIN device ON customerLocation.lid_id = device.lid_id)"
                       + " JOIN data ON device.did = data.did"
                       +  f" WHERE cid_id = {cid} AND label = 'energy use'"
                       + " GROUP BY DATE_TRUNC('DAY', timestamp), device.did"
                       + " ORDER BY DATE_TRUNC('DAY', timestamp), device.did")
        
        deviceDailyEnergyUse= {}

        for d in cursor.fetchall():
            if d[1] not in deviceDailyEnergyUse.keys():
                deviceDailyEnergyUse[d[1]] = {'time_labels' : [d[0].strftime('%m-%d-%Y')],
                'values' : [float(d[2])]}
            else:
                deviceDailyEnergyUse[d[1]]['time_labels'].append(d[0].strftime('%m-%d-%Y'))
                deviceDailyEnergyUse[d[1]]['values'].append(float(d[2]))

    return deviceDailyEnergyUse

'''
Gets the energy usage of different device types 
at a particular location for the current month
'''
def getDeviceTypeEnergyUsage(cid, year, month):
    with connection.cursor() as cursor: 
        cursor.execute(f"SELECT device.lid_id, model_type, SUM(value)"
                       + " FROM ((customerLocation JOIN device ON customerLocation.lid_id=device.lid_id)"
                       + " JOIN model ON device.model_num_id = model.model_num) JOIN data ON device.did=data.did"
                       + f" WHERE cid_id = {cid} AND label = 'energy use'"
                       + f" AND EXTRACT(MONTH FROM data.timestamp) = {month}"
                       + f" AND EXTRACT(YEAR FROM data.timestamp) = {year}"
                       + " GROUP BY device.lid_id, model_type")
        locations = {} 
        for row in cursor.fetchall():
            if row[0] not in locations.keys():
                locations[row[0]] = {'model_type': [row[1]], 'energy_use':[float(row[2])]}
            else:
                locations[row[0]]['model_type'].append(row[1])
                locations[row[0]]['energy_use'].append(float(row[2]))

    return locations


'''
Gets the energy prices of the customer's service locations
'''
def getEnergyPrice(cid, year, month):
    with connection.cursor() as cursor:
        cursor.execute("SELECT EXTRACT(HOUR FROM date_time), EnergyPrice.zipcode, AVG(price_per_hr)"
                       + " FROM (CustomerLocation JOIN Location ON CustomerLocation.lid_id=Location.lid)" 
                       + " JOIN EnergyPrice ON Location.zipcode = EnergyPrice.zipcode"
                       + f" WHERE cid_id = {cid} AND EXTRACT(MONTH FROM date_time) = {month}"
                       + f" AND EXTRACT(YEAR FROM date_time) = {year}"
                       + " GROUP BY EXTRACT(HOUR FROM date_time), EnergyPrice.zipcode"
                       + " ORDER BY EXTRACT(HOUR FROM date_time)")
        zipcodes = {}
        for row in cursor.fetchall():
            if row[1] not in zipcodes.keys():
                print(row[0])
                zipcodes[row[1]] = {'date': [int(row[0])], 
                                    'price': [float(row[2])]}
            else:
                zipcodes[row[1]]['date'].append(int(row[0]))
                zipcodes[row[1]]['price'].append(float(row[2]))
    return zipcodes


'''
Gets the total energy usage each month this year by location
'''
def getTotalEnergyUsageByLocation(cid, year, month):
    with connection.cursor() as cursor: 
        cursor.execute(f"SELECT customerLocation.lid_id, EXTRACT(MONTH FROM data.timestamp) as month, SUM(value)"
                       + " FROM (customerLocation JOIN device ON customerLocation.lid_id = device.lid_id)"
                       + " JOIN data ON device.did = data.did"
                       + f" WHERE cid_id = {cid} AND label = 'energy use'"
                       + f" AND EXTRACT(YEAR FROM data.timestamp) = {year}"
                       + " GROUP BY customerLocation.lid_id, EXTRACT(MONTH FROM data.timestamp)"
                       + " ORDER BY EXTRACT(MONTH from data.timestamp)")
        locations = {} 
        months = ["January", "February", "March", "April", "May", 
                  "June", "July", "August", "September", "October", "November",
                  "December"]
        totalEnergy = [0 for i in range(month)]
        months = months[:month]

        for row in cursor.fetchall():
            if (int(row[1]) > month):
                continue
            if row[0] not in locations.keys():
                locations[row[0]] = totalEnergy.copy()
                locations[row[0]][int(row[1]) - 1] = float(row[2])
            else:
                locations[row[0]][int(row[1]) - 1] = locations[row[0]][int(row[1]) - 1] + float(row[2])
        totalEnergyUsage = {'locations': locations, 'months': months}
    return totalEnergyUsage
