from django import forms
from .models import MessageInquiry

class MessageInquiryForm(forms.ModelForm):
    class Meta:
        model = MessageInquiry
        fields = ['message_text']
        widgets = {
            'message_text': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Ask the owner about availability or negotiate prices directly...'}),
        }