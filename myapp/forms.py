from django import forms
from .models import *
class loginForm(forms.ModelForm):
    class Meta:
        model=login_tbl
        fields='__all__'
class changepassForm(forms.ModelForm):
    class Meta:
        model =login_tbl
        fields=['password']
class profileForm(forms.ModelForm):
    class Meta:
        model=login_tbl
        fields=['username','email','mobile','image','firstname','lastname']
class profileditForm(forms.ModelForm):
    class Meta:
        model=login_tbl
        fields=['username','email','mobile','image','fullname']
class InsuranceForm(forms.ModelForm):
    class Meta:
        model = Insurance
        fields = '__all__'
        unique_together = ('name', 'policy_number')
        widgets = {
            'entry_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'risk_date': forms.DateInput(attrs={'type': 'date'}),
            
        }
class CompanyReportForm(forms.Form):
    insurance_company = forms.ChoiceField(
        choices=[('', 'All Companies')] + [(c, c) for c in Insurance.objects.values_list('insurance_company', flat=True).distinct()],
        required=False,
        label='Insurance company'
    )
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
class BranchReportForm(forms.Form):
    start_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        branches = Insurance.objects.values_list('location', flat=True).distinct()
        branch_choices = [('', 'All Branches')] + [(b, b) for b in branches]
        self.fields['branch'] = forms.ChoiceField(
            choices=branch_choices,
            required=False,
            widget=forms.Select(attrs={'class': 'form-select'})
        )

class ReportFilterForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    
    # Dynamically populate location choices
    location = forms.ChoiceField(
        required=False,
        choices=[],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        locations = Insurance.objects.values_list('location', flat=True).distinct()
        cleaned_locations = sorted(set(loc.split('-')[0].strip() for loc in locations if loc))
        self.fields['location'].choices = [('', 'All Branches')] + [(loc, loc) for loc in cleaned_locations]
class PolicyHistoryForm(forms.Form):
    
    client_name = forms.ChoiceField(choices=[], required=True)
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



        # Dynamic Client Choices (will be refined by branch in view if needed)
        clients = Insurance.objects.values_list('client_name', flat=True).distinct().order_by('client_name')
        self.fields['client_name'].choices = [('', 'Select Client')] + [(c, c) for c in clients]

class AgentCommissionFilterForm(forms.Form):
    agent_name = forms.ChoiceField(choices=[], required=False)
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        agents = Insurance.objects.values_list('agent_name', flat=True).distinct()
        self.fields['agent_name'].choices = [('', 'All Agents')] + [(agent, agent) for agent in agents]
class CSVUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedCSV
        fields = ['file']

class AdduserForm(forms.ModelForm):
    class Meta:
        model= login_tbl
        fields='__all__'  
