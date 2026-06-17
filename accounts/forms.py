from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, NationalIDVerification

class MarketplaceUserCreationForm(UserCreationForm):
    """
    🔧 FIXED: Renamed to perfectly match your register_view component.
    Converts blank phone/ID strings to real database NULL entries to prevent crashes.
    """
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'phone_number', 'national_id']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., +263771234567'}),
            'national_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 63-123456X78'}),
        }

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not phone:
            return None  # Forces true database NULL instead of an empty string duplicate
            
        # Standardise local 07... mobile formats into standard country codes on submission
        if phone.startswith('07'):
            phone = '+263' + phone[1:]
        return phone

    def clean_national_id(self):
        nid = self.cleaned_data.get('national_id')
        if not nid:
            return None  # Forces true database NULL instead of an empty string duplicate
        return nid


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