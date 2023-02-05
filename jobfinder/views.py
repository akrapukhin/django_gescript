from django.shortcuts import render
from .models import ViewCounter
import datetime
# Create your views here.

from jobfinder.jobfinder import find_vacancies
from jobfinder.forms import QueryForm
from datetime import datetime
from django.db.models import F
def query(request):
    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = QueryForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            #request.session['included_areas'] = form.cleaned_data['include_areas']
            query = form.cleaned_data['query_text']
            request.session['query'] = query
            areas, areas_ids, areas_str = form.cleaned_data['include_areas']
            request.session['areas'] = areas
            excluded_areas, excluded_areas_list, excluded_areas_str = form.cleaned_data['exclude_areas']
            request.session['excluded_areas'] = excluded_areas
            date_from = form.cleaned_data['from_date']
            print("form date_from:", date_from, type(date_from))
            if date_from is not None:
                date_from = date_from.strftime("%d-%m-%Y")
            request.session['date_from'] = date_from
            exclude_quota = form.cleaned_data['exclude_quota']
            request.session['exclude_quota'] = exclude_quota
            num_vacancies, num_of_vacancies_total, vacancies_list, query_str, date_str, num_of_comp_str, warning2000, warning_not_excluded, warning_quota = find_vacancies(query, areas, excluded_areas, date_from, areas_ids, areas_str, excluded_areas_list, excluded_areas_str, exclude_quota)
            print("vacancies_list size:", len(vacancies_list))
            context = {
                'num_vacancies': num_vacancies,
                'num_of_vacancies_total': num_of_vacancies_total,
                'included_areas': areas_str,
                'excluded_areas': excluded_areas_str,
                'query': query_str,
                'date': date_str,
                'num_of_comp': num_of_comp_str,
                'vacancies': vacancies_list,
                'warning2000': warning2000,
                'warning_not_excluded' : warning_not_excluded,
                'warning_quota': warning_quota,
            }
            counter = ViewCounter.objects.filter(name='totalCounter')
            counter.update(counter=F('counter') + 1)
            return render(request, 'results.html', context)

    # If this is a GET (or any other method) create the default form
    else:
        query_text = request.session.get('query', None)
        include_areas = request.session.get('areas', None)
        exclude_areas = request.session.get('excluded_areas', None)
        from_date = request.session.get('date_from', None)
        excl_quota = request.session.get('exclude_quota', None)
        if query_text is None and include_areas is None and exclude_areas is None and from_date is None and excl_quota is None:
            counter = ViewCounter.objects.filter(name='uniqueCounter')
            counter.update(counter=F('counter') + 1)
        form = QueryForm(initial={'query_text': query_text, 'include_areas': include_areas, 'exclude_areas': exclude_areas, 'from_date': from_date, 'exclude_quota': excl_quota})

    context = {
        'form': form,
    }
    return render(request, 'query_page_crispy.html', context)

def counters(request):
    total = ViewCounter.objects.get(name='totalCounter').counter
    unique = ViewCounter.objects.get(name='uniqueCounter').counter
    context = {
        'total': total,
        'unique': unique,
    }
    return render(request, 'counters.html', context)
