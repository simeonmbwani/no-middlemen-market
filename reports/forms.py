from django import forms

class DirectReportForm(forms.Form):
    """
    A model-free reporting form.
    Gathers information safely on-the-fly without importing or saving database tables.
    """
    REASON_CHOICES = [
        ('middleman', 'Agent / Broker pretending to be the Legal Owner'),
        ('fraud', 'Scam / Extortion / Fake contact details'),
        ('duplicate', 'Duplicate asset listed by multiple accounts'),
        ('illegal', 'Prohibited items or unlicensed commercial activity'),
    ]

    reason = forms.ChoiceField(
        choices=REASON_CHOICES, 
        label="Reason for flagging",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    details = forms.CharField(
        label="Supporting details",
        max_length=500,
        widget=forms.Textarea(attrs={
            'rows': 3, 
            'class': 'form-control',
            'placeholder': 'Please state exactly why you believe this user is a broker or scammer...'
        })
    )