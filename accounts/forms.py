from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from .models import NationalIDVerification

class OwnerRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'phone_number', 'national_id']
        widgets = {
            'phone_number': forms.TextInput(attrs={'placeholder': 'e.g., +263771234567'}),
            'national_id': forms.TextInput(attrs={'placeholder': 'e.g., 63-123456X78'}),
        }

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        # Simple parsing to standardise 07... numbers to +263 format on submission
        if phone.startswith('07'):
            phone = '+263' + phone[1:]
        return phone

class NationalIDUploadForm(forms.ModelForm):
    class Meta:
        model = NationalIDVerification
        fields = ['id_document_front', 'id_document_back']
        labels = {
            'id_document_front': 'National ID Card (Front Side)',
            'id_document_back': 'National ID Card (Back Side - Optional)',
        }
        widgets = {
            'id_document_front': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'id_document_back': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }    