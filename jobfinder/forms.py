from django.core.exceptions import ValidationError
import datetime  # for checking renewal date range.
from django import forms
import requests

class QueryForm(forms.Form):
    query_text = forms.CharField(widget=forms.Textarea(attrs={'rows':2}), label="Запрос:", help_text="*Обязательное поле")
    include_areas = forms.CharField(widget=forms.Textarea(attrs={'rows':2, 'placeholder': 'По умолчанию — вся Россия'}), label="Города и области поиска:", required=False, help_text = "Каждый город или область на отдельной строке")
    exclude_areas = forms.CharField(widget=forms.Textarea(attrs={'rows':2}), label="Исключаемые города:", required=False)
    from_date = forms.DateField(widget=forms.DateInput(format="%d-%m-%Y", attrs={'placeholder': 'По умолчанию — все активные вакансии'}), label="Ограничение по дате:", help_text="Формат: ДД-ММ-ГГГГ", required=False, input_formats=['%d-%m-%Y'])
    exclude_quota = forms.BooleanField(label="Убрать вакансии, требующие места в квоте", required=False)

    russia_areas = []
    russia_id = 113
    all_areas = requests.get('https://api.hh.ru/areas')
    all_areas = all_areas.json()
    for area in all_areas:
	    if area['name'].lower() == 'россия':
	        russia_id = area['id']
	        russia_areas = area['areas']
    
    def clean_from_date(self):
        data = self.cleaned_data['from_date']
        # Check date
        if data is not None:
            if data > datetime.date.today():
                raise ValidationError('Дата не может быть в будущем.')
        return data

    def clean_query_text(self):
        data = self.cleaned_data['query_text']
        if data is not None:
            data_check = data
            data_check = data_check.split()
            if len(data_check) > 1:
                if data_check[-1].strip().lower() == "or":
                    raise ValidationError('Запрос не должен заканчиваться на "OR".')
        return data
        
    def clean_include_areas(self):
        data = self.cleaned_data['include_areas']
        areas = data
        areas = areas.splitlines()
        areas_list = []
        for area in areas:
            area = area.strip().lower()
            if area != '':
                areas_list.append(area)
                
        # find corresponding areas IDs
        areas_ids = []
        areas_str = ""
        if len(areas_list) == 0:
            areas_ids.append(self.russia_id)
            areas_list.append("Россия")
            areas_str = "Россия"
        else:
            for area in areas_list:
                area_found = False
                for region in self.russia_areas:
                    if region['name'].lower() == area.lower():
                        areas_ids.append(region['id'])
                        area_found = True
                        areas_str += region['name'] + ", "
                    for city in region['areas']:
                        if city['name'].lower() == area.lower():
                            areas_ids.append(city['id'])
                            area_found = True
                            areas_str += city['name'] + ", "
                if not area_found:
                    raise ValidationError('Территория не найдена: ' + area)
        areas_str = areas_str.strip()
        if areas_str[-1] == ",":
            areas_str = areas_str[:-1]
        return data, areas_ids, areas_str

    def clean_exclude_areas(self):
        data = self.cleaned_data['exclude_areas']
        excluded_areas = data
        excluded_areas = excluded_areas.splitlines()
        excluded_areas_list = []
        excluded_areas_str = "-"
        for area in excluded_areas:
            area = area.strip().lower()
            if area != '':
                excluded_areas_list.append(area)

        # check excluded cities
        for excl_area in excluded_areas_list:
            area_found = False
            for region in self.russia_areas:
                if region['name'].lower() == excl_area.lower():
                    if excl_area.lower() == "москва" or excl_area.lower() == "санкт-петербург":
                        area_found = True
                        excluded_areas_str += region['name'] + ", "
                for city in region['areas']:
                    if city['name'].lower() == excl_area.lower():
                        area_found = True
                        excluded_areas_str += city['name'] + ", "
            if not area_found:
                raise ValidationError('Город не найден: ' + area)

        excluded_areas_str = excluded_areas_str.strip()
        if excluded_areas_str[-1] == ",":
            excluded_areas_str = excluded_areas_str[1:-1]  # index from 1 to eliminate '-'
        return data, excluded_areas_list, excluded_areas_str
