from django import forms
from .models import Listing, InvestorLead

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        # We exclude 'realtor' and 'list_date' because they are handled automatically
        exclude = ('realtor', 'list_date')
        
        # Adding Bootstrap classes to make the form look professional
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Property Title'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'zipcode': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'expectations': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'eligibility_criteria': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'bond': forms.NumberInput(attrs={'class': 'form-control'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'bathrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'realtor_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_pet_friendly': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }



class InvestorRequestForm(forms.ModelForm):
    class Meta:
        model = InvestorLead
        fields = ['full_name', 'email', 'phone', 'organization', 'investor_type', 'linkedin_profile', 'message', 'is_accredited']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Jane Doe'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'jane@capitalfirm.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+61 ...'}),
            'organization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Acme Capital'}),
            'investor_type': forms.Select(attrs={'class': 'form-select'}),
            'linkedin_profile': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/...'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'We focus on early-stage regional tech...'}),
            'is_accredited': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }