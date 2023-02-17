import requests
from bs4 import BeautifulSoup
from fake_headers import Headers
import json

def get_headear():
    headers = Headers(browser='chrome', os='win')
    return headers.generate()

response = requests.get('https://spb.hh.ru/search/vacancy?text=python&area=1&area=2', headers=get_headear())
hh_main = response.text
soup = BeautifulSoup(hh_main, features='lxml')

vacancy_list = soup.find('div', class_= 'vacancy-serp-content')
vacancy = vacancy_list.find_all('div', class_='serp-item')


def search_info(link):
    response_v = requests.get(link, headers=get_headear())
    hh_vac = BeautifulSoup(response_v.text, features='lxml')
    tag_title = hh_vac.find('div',  class_='vacancy-title')
    salary = tag_title.select_one('[data-qa=vacancy-salary-compensation-type-undefined]')
    if salary is None:
        salary = tag_title.select_one('[data-qa=vacancy-salary-compensation-type-gross]')
    elif salary is None:
        salary = tag_title.select_one('[data-qa=vacancy-salary-compensation-type-net]')
    tag_comp = hh_vac.find('div',  class_='bloko-columns-row')
    employer = tag_comp.select_one('[data-qa=bloko-header-2]').get_text()
    location = tag_comp.select_one('[data-qa=vacancy-view-location]')
    if location is None:
        location = tag_comp.select_one('[data-qa=vacancy-view-raw-address]')
    return salary, employer, location

def search_vacancy(vacancy):
    check = ['Django', 'django', 'Flask', 'flask']
    parced = []
    links = []
    for vac in vacancy:
        user_tag = vac.find('div', class_='g-user-content')
        tag = user_tag.select('.bloko-text')
        description = []
        for t in tag:
            desc = t.get_text()
            description.append(desc)
        for el in check:
            if el in ','.join(description):
                header = vac.find('h3')
                a_tag = header.find('a')
                link = a_tag['href']
                salary, employer, location = search_info(link)

                item = {
                    'link': link,
                    'salary': salary.get_text(),
                    'employer': employer,
                    'location': location.get_text()
                }

                if link not in links:
                    parced.append(item)
                    links.append(link)
                    
    if bool(parced) is False:
        print('Вакансий по заданным параметром не найдено')
    else:
        return parced


if __name__ == '__main__':
    with open ('vacancy.json', 'w', encoding='utf-8') as file:
        json.dump(search_vacancy(vacancy), file, ensure_ascii=False)


