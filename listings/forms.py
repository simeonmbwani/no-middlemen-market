from django import forms
from .models import Listing

class ListingForm(forms.ModelForm):
    """
    Upgraded, dynamic form for asset creation.
    Injects theme-friendly CSS configurations and placeholder layouts.
    """
    class Meta:
        model = Listing
        fields = [
            'title', 'category', 'description', 'price', 
            'province', 'district', 'image1', 'image2', 'image3'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 🎨 Dynamically style every input field to look modern and crisp
        for field_name, field in self.fields.items():
            if field_name in ['category', 'province']:
                field.widget.attrs.update({'class': 'form-select form-select-md border-2'})
            elif field_name in ['image1', 'image2', 'image3']:
                field.widget.attrs.update({'class': 'form-control form-control-sm border-dashed'})
            else:
                field.widget.attrs.update({'class': 'form-control border-2'})
        
        # Specific placeholders for localized contexts
        self.fields['title'].widget.attrs.update({'placeholder': 'e.g., 3-Phase Gold Ball Mill'})
        self.fields['district'].widget.attrs.update({'placeholder': 'e.g., Kadoma, Shurugwi, Gwanda'})
        self.fields['description'].widget.attrs.update({
            'placeholder': 'Specify terms, capacity, runtime hours, and inclusion criteria...',
            'rows': 4
        })