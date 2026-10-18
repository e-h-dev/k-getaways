from django import forms
from .models import Survey


class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ['were_you_contacted',
            'if_yes_how_many_times_where_you_contacted',
            'have_you_confirmed_any_bookings',
            'if_yes_how_many_bookings',
            'how_was_your_overall_experiance_with_KosherGetaways',
            'how_likely_are_you_to_recommend_KosherGetaways',
            'if_you_have_any_suggestions_please_enter_below',
            'any_other_comments',
            'email']

        widgets = {
            'were_you_contacted': forms.RadioSelect(attrs={'class': 'pricing-radio'}),
            'have_you_confirmed_any_bookings': forms.RadioSelect(attrs={'class': 'pricing-radio'}),
            'how_was_your_overall_experiance_with_KosherGetaways' : forms.RadioSelect(attrs={'class': 'pricing-radio'}),
            'how_likely_are_you_to_recommend_KosherGetaways' : forms.RadioSelect(attrs={'class': 'pricing-radio'}),
        }

    def __init__(self, *args, **kwargs):
        super(SurveyForm, self).__init__(*args, **kwargs)

        were_you_contacted_label = ", about you listing?"
        have_you_confirmed_any_bookings_label = "?"
                
        self.fields['were_you_contacted'].label = f"{self.fields['were_you_contacted'].label}{were_you_contacted_label}"
        self.fields['have_you_confirmed_any_bookings'].label = f"{self.fields['have_you_confirmed_any_bookings'].label}{have_you_confirmed_any_bookings_label}"
                