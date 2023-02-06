import requests
import codecs
import urllib.request
import webbrowser
import time
import os
import threading
import wget

class MyWorker():
    def __init__(self):
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        url = "https://файлы.президентскиегранты.рф/81cf9ab5-07f9-4272-a058-ec578b4e4c61"
        file = wget.download(url)


def load_companies(path):
    companies = []
    companies_file = codecs.open(path, 'r', 'utf-8')
    companies_lines = companies_file.readlines()
    for line in companies_lines:
        line = line.strip().lower()
        if line != '':
            companies.append(line)
    companies = set(companies)
    companies = list(companies)
    comp_ids = []
    for s in companies:
        comp_ids.append(s[23:])
    return comp_ids

def find_vacancies(query, areas, excluded_areas, date_from, areas_ids, areas_str, excluded_areas_list, excluded_areas_str, exclude_quota):
    start_time = time.time()
    # read query from file
    query = query.split()
    query_string = ""
    for word in query:
        query_string += word.strip() + " "
    query_string = query_string.strip()
    
    # read date from file
    date_from_format_day_first = "-"
    if date_from is not None and len(date_from) > 0:
        if len(date_from) != 10 or date_from[2] != '-' or date_from[5] != '-':
            print("Ошибка: неверно введена дата в файле date_from.txt. Правильный формат: ДД-ММ-ГГГГ. Пример: 01-02-2020")
            print("Можете также убрать ограничение по дате, удалив все из файла date_from.txt")
            exit()
        else:
            date_from_format_day_first = date_from
            date_from = date_from[6:10] + date_from[5] + date_from[3:5] + date_from[2] + date_from[0:2]
    else:
        date_from = None
    
    # load list of companies
    main_ids = load_companies('companies/main.txt')
    sk_ids = load_companies('companies/skolkovo.txt')
    p218_ids = load_companies('companies/p218.txt')
    mordovia_ids = load_companies('companies/technoparks/mordovia.txt')
    zhigul_ids = load_companies('companies/technoparks/zhigul.txt')
    universitet_ids = load_companies('companies/technoparks/universitet.txt')
    fizteh_ids = load_companies('companies/technoparks/fizteh.txt')
    khimgrad_ids = load_companies('companies/technoparks/khimgrad.txt')
    it_park_kazan_ids = load_companies('companies/technoparks/it_park_kazan.txt')
    it_park_nab_cheln_ids = load_companies('companies/technoparks/it_park_nab_cheln.txt')
    rameev_ids = load_companies('companies/technoparks/rameev.txt')
    kuzbass_ids = load_companies('companies/technoparks/kuzbass.txt')
    akadempark_ids = load_companies('companies/technoparks/akadempark.txt')
    zapsib_ids = load_companies('companies/technoparks/zapsib.txt')
    ankudinovka_ids = load_companies('companies/technoparks/ankudinovka.txt')
    only_moscow_ids = load_companies('companies/only_moscow.txt')
    only_spb_ids = load_companies('companies/only_spb.txt')

    companies_ids = main_ids + sk_ids + p218_ids + mordovia_ids + zhigul_ids + universitet_ids + fizteh_ids + khimgrad_ids + it_park_kazan_ids + it_park_nab_cheln_ids + rameev_ids + kuzbass_ids + akadempark_ids + zapsib_ids + ankudinovka_ids
    companies_ids = set(companies_ids)
    companies_ids = list(companies_ids)
    
    # parameters of query to hh
    if query_string == "-":
        query_string = ""
    par = {'text': query_string,
           'area': areas_ids,
           'per_page': '100',
           'employer_id': companies_ids,
           'order_by': 'publication_time',
           'date_from': date_from,
           'page': 0}
    
    if query_string == "":
        query_string = "-"
    # request to hh to get all vacancies
    all_pages = []
    print()
    print("|||||||||||||||||||||||||||||||||||")
    print("LS:", os.listdir())
    print("query:", query_string)
    with open("test.txt", "a") as file_object:
        file_object.write(f"{time.time()}\n")
    print("TRUDVSEM", requests.get(f"http://opendata.trudvsem.ru/api/v1/vacancies/company/inn/7726700943"))
    print("areas:", areas)
    print("excluded_areas:", excluded_areas_list)
    print("date_from:", date_from)
    print("exclude_quota:", exclude_quota)
    with open("test.txt", "r") as file_object:
        for line in file_object.readlines():
            print(line.strip())
    print("|||||||||||||||||||||||||||||||||||")
    print()
    start_req_time = time.time()
    first_page_vacancies = requests.get('https://api.hh.ru/vacancies', params=par, timeout=120)
    print("Запрос отправлен. Подождите несколько секунд...")
    if str(first_page_vacancies)[11:14] != "200":
        print("HH RESPONSE NOT OK!", str(first_page_vacancies)[:14])
        exit()

    first_page_vacancies = first_page_vacancies.json()
    all_pages.append(first_page_vacancies)
    
    num_of_vacancies_total = first_page_vacancies['found']
    num_of_vacancies = first_page_vacancies['found']
    if num_of_vacancies > 2000:
        num_of_vacancies = 2000
    num_of_pages = first_page_vacancies['pages']
    
    for page_num in range(num_of_pages - 1):
        par['page'] = page_num + 1
        page_vacancies = requests.get('https://api.hh.ru/vacancies', params=par, timeout=120)
        page_vacancies = page_vacancies.json()
        all_pages.append(page_vacancies)
        print(page_num, time.time() - start_req_time)
    stop_req_time = time.time()
    
    counter = 1
    vacancies_list = []
    for page in all_pages:
        vacancies = page['items']
        for vac in vacancies:
            excluded = False
            quota_required = False
            reason = ""
            for excluded_area in excluded_areas_list:
                if excluded_area.lower() == vac['area']['name'].lower():
                    excluded = True
            if (vac['employer']['id'] in only_moscow_ids) and not (vac['area']['name'].lower() == 'москва' or vac['area']['name'].lower() == 'зеленоград'):
                quota_required = True
                reason = "компания зарегистрирована в Москве"
            if (vac['employer']['id'] in only_spb_ids) and not (vac['area']['name'].lower() == 'санкт-петербург'):
                quota_required = True
                reason = "компания зарегистрирована в Санкт-Петербурге"
            if quota_required and (vac['area']['name'].lower() == 'москва' or vac['area']['name'].lower() == 'зеленоград' or vac['area']['name'].lower() == 'санкт-петербург'):
                quota_required = False
            if vac['area']['name'].lower() == 'зеленоград':
                quota_required = True
                reason = "Зеленоград входит в состав Москвы"
            if quota_required and exclude_quota:
                excluded = True
            if not excluded:
                # get salary
                salary = vac['salary']
                salary_str = ""
                if salary is None:
                    salary_str = "не указана"
                else:
                    if salary['from'] is not None:
                        salary_str = "от " + str(salary['from']) + " "
                    if salary['to'] is not None:
                        salary_str += "до " + str(salary['to'])
                    if salary['gross']:
                        salary_str += " до вычета"
                    else:
                        salary_str += " на руки"
                # get logo
                logo_str = ""
                if vac['employer']['logo_urls'] is not None:
                    if '90' in vac['employer']['logo_urls']:
                        if vac['employer']['logo_urls']['90'] is not None:
                            logo_str = vac['employer']['logo_urls']['90']
    
                vac_info = {}
                vac_info['num'] = counter
                vac_info['title'] = vac['name']
                vac_info['employer_name'] = vac['employer']['name']
                vac_info['logo'] = logo_str
                vac_info['area'] = vac['area']['name']
                vac_info['salary'] = salary_str
                vac_info['time'] = vac['published_at'][8:10] + vac['published_at'][7] + vac['published_at'][5:7] + vac['published_at'][4] + vac['published_at'][0:4] + " " + vac['published_at'][11:16]
                vac_info['url'] = vac['alternate_url']
                vac_info['shown_url'] = vac['alternate_url'][8:]
                vac_info['emp_url'] = vac['employer']['alternate_url']
                vac_info['in_main'] = vac['employer']['id'] in main_ids
                vac_info['in_sk'] = vac['employer']['id'] in sk_ids
                vac_info['in_p218'] = vac['employer']['id'] in p218_ids
                vac_info['in_mordovia'] = vac['employer']['id'] in mordovia_ids
                vac_info['in_zhigul'] = vac['employer']['id'] in zhigul_ids
                vac_info['in_universitet'] = vac['employer']['id'] in universitet_ids
                vac_info['in_fizteh'] = vac['employer']['id'] in fizteh_ids
                vac_info['in_khimgrad'] = vac['employer']['id'] in khimgrad_ids
                vac_info['in_it_park_kazan'] = vac['employer']['id'] in it_park_kazan_ids
                vac_info['in_it_park_nab_cheln'] = vac['employer']['id'] in it_park_nab_cheln_ids
                vac_info['in_rameev'] = vac['employer']['id'] in rameev_ids
                vac_info['in_kuzbass'] = vac['employer']['id'] in kuzbass_ids
                vac_info['in_akadempark'] = vac['employer']['id'] in akadempark_ids
                vac_info['in_zapsib'] = vac['employer']['id'] in zapsib_ids
                vac_info['in_ankudinovka'] = vac['employer']['id'] in ankudinovka_ids
                vac_info['quota_required'] = quota_required
                vac_info['reason'] = reason
                vacancies_list.append(vac_info)
                counter += 1
                
            else:
                num_of_vacancies -= 1
    
    warning2000 = False
    if num_of_vacancies_total > 2000:
        warning2000 = True
    
    excluded_areas_list_small = []
    for a in excluded_areas_list:
        excluded_areas_list_small.append(a.lower())

    warning_not_excluded = False
    warning_quota = False

    moscow_excluded = 'москва' in excluded_areas_list_small
    spb_excluded = 'санкт-петербург' in excluded_areas_list_small

    if exclude_quota and not (moscow_excluded and spb_excluded):
        warning_not_excluded = True

    if not exclude_quota and (moscow_excluded or spb_excluded):
        warning_quota = True

    print("find_vacancies() time:", time.time() - start_time)
    print("req time:", stop_req_time - start_req_time)
    print("num_of_vacancies_total", num_of_vacancies_total)
    print("num_of_pages:", num_of_pages)
    print("before MyWorker()")
    MyWorker()
    print("after MyWorker()")
    return num_of_vacancies, num_of_vacancies_total, vacancies_list, query_string, date_from_format_day_first, str(len(companies_ids)), warning2000, warning_not_excluded, warning_quota
    
