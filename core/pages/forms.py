
from django.shortcuts import render, redirect
from django.contrib import messages
# ADD THIS LINE BELOW:
from listings.forms import InvestorRequestForm
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