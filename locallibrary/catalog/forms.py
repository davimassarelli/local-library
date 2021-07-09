import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(help_text="Insira uma data entre hoje e 4 semanas (padrão 3).")

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        # Checar se a data está no passado.
        if data < datetime.date.today():
            raise ValidationError(_('Data inválida - Renovação no passado'))

        # Checar se a data está fora do período permitido (+4 semanas a partir de hoje).
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Data inválida - renovação com mais de 4 semanas'))

        # Lembrar de sempre retornar o campo vazio
        return data
