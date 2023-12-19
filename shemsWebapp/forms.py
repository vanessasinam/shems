from django import forms
from django.forms import ModelForm, ValidationError
from django.contrib.auth.models import User
from .models import (
    Customer,
    Location,
    Device,
    DeviceModel
)
from django.db import connection

class CustomerForm(ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "first name"})
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "last name"})
    )
    billing_address = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "billing address"})
    )
    class Meta:
        model = Customer
        fields= ["first_name", "last_name", "billing_address"]
    
    def save(self, commit=True):
        customer = super(CustomerForm, self).save(commit=False)
        if commit:
            customer.save()
        return customer

class LocationForm(ModelForm):
    num_bedrooms = forms.IntegerField(
        widget=forms.TextInput(attrs={"placeholder": "number of bedrooms"})
    )
    num_occupants = forms.IntegerField(
        widget=forms.TextInput(attrs={"placeholder": "number of occupants"})
    )
    area = forms.IntegerField(
        widget=forms.TextInput(attrs={"placeholder": "area"})
    )
    unit = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "unit"})
    )
    street = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "street"})
    )
    building = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "building"})
    )  
    city = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "city"})
    ) 
    zipcode = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "zipcode"})
    ) 
    class Meta:
        model = Location
        fields= ["num_bedrooms", "num_occupants", "area", "unit", 
                 "street", "building", "city", "zipcode"]
    
    def save(self, commit=True):
        location = super(LocationForm, self).save(commit=False)
        if commit:
            location.save()
        return location

class DeviceForm(ModelForm):
    DEVICE_TYPES = (
        ('All','All'),
        ('Refrigerator', 'Refrigerator'),
        ('Dryer', 'Dryer'),
        ('Washing machine', 'Washing machine'),
        ('Television', 'Television'),
        ('AC system', 'AC system'),
        ('Light', 'Light')
    )
    lid = forms.ModelChoiceField(queryset=Location.objects.none(), empty_label='Select a location')
    model_type = forms.ChoiceField(choices=DEVICE_TYPES, required=False)

    class Meta:
        model = Device
        fields= ["lid", "model_type", "model_num"]
            
    def save(self, commit=True):
        device = super(DeviceForm, self).save(commit=False)
        if commit:
            device.save()
        return device

    def __init__(self, *args, **kwargs):   
        lids = kwargs.pop('lids')   
        super(DeviceForm, self).__init__(*args, **kwargs)
        if lids:
            self.fields['lid'] = forms.ModelChoiceField(
                queryset=Location.objects.filter(lid__in=lids),
                empty_label='Select a location'
            )

        if 'model_type' in self.data:
            try:
                model_type = int(self.data.get('model_type'))
                if 'model_type' == "All" :
                    self.fields['model_num'].queryset = DeviceModel.objects.all()
                else:
                    self.fields['model_num'].queryset = DeviceModel.objects.filter(model_type=model_type)
                self.fields['model_num'].empty_label = 'Select a model'
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['model_num'].queryset = self.Location.objects.none()

