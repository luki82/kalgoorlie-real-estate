from django import forms
from .models import Listing, InvestorLead

# --- 1. LISTING CREATION FORM ---
class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        # We exclude 'realtor' and 'list_date' because they are handled automatically
        exclude = ('realtor', 'list_date', 'is_published')
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Property Title'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'zipcode': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'expectations': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'What are your expectations for a tenant?'}),
            'eligibility_criteria': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'bond': forms.NumberInput(attrs={'class': 'form-control'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'bathrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'realtor_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'is_pet_friendly': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'photo_main': forms.FileInput(attrs={'class': 'form-control'}),
            'photo_1': forms.FileInput(attrs={'class': 'form-control'}),
            'photo_2': forms.FileInput(attrs={'class': 'form-control'}),
            'photo_3': forms.FileInput(attrs={'class': 'form-control'}),
            'photo_4': forms.FileInput(attrs={'class': 'form-control'}),
        }

# --- 2. INVESTOR REQUEST FORM ---
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

# --- 3. CONTACT AGENT FORM (New!) ---
class ContactAgentForm(forms.Form):
    # Choices for "About Me"
    ABOUT_CHOICES = [
        ('I own my home', 'I own my home'),
        ('I am a first home buyer', 'I am a first home buyer'),
        ('I am renting', 'I am renting'),
        ('I am an investor', 'I am an investor'),
        ('I have recently sold', 'I have recently sold'),
        ('I am monitoring the market', 'I am monitoring the market'),
    ]

    # Choices for "Interested In"
    INTEREST_CHOICES = [
        ('Date available', 'Date available'),
        ('Length of lease', 'Length of lease'),
        ('Home open times', 'Home open times'),
        ('Parking availability', 'Parking availability'),
        ('Pets allowed', 'Pets allowed'),
        ('Rental application', 'Rental application'),
    ]

    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name *'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name *'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email *'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}))
    
    # Radio Buttons for About Me
    about_me = forms.ChoiceField(
        choices=ABOUT_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'list-unstyled'}),
        initial='I own my home'
    )

    # Checkboxes for Interests
    interests = forms.MultipleChoiceField(
        choices=INTEREST_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'list-unstyled'}),
        required=False
    )

    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Hi, I found this property...'}),
        required=True
    )