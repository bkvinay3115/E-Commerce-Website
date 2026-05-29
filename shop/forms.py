from django import forms


class AddressForm(forms.Form):
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        label="Delivery Address"
    )

    payment_method = forms.ChoiceField(
        choices=[
            ('COD', 'Cash on Delivery'),
            ('ONLINE', 'Online Payment')
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Payment Method"
    )


class FeedbackForm(forms.Form):
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    comment = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )
