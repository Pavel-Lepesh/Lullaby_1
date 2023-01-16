import requests as rq
from bs4 import BeautifulSoup
import csv

def cooking_soup(link: str):
    '''For quick using "soup"'''
    response = rq.get(url=link)
    response.encoding = 'utf-8'
    return BeautifulSoup(response.text, 'lxml')


def get_minus(minus, x):  # получаем минус
    a = minus.find('audio')['data-src']
    minus_file = a.split('/')[-1].strip('.mp3') + f'_{x}_minus.mp3'
    link = 'https://xn----9sbmabsiicuddu3a5lep.xn--p1ai' + a
    resp = rq.get(link)
    try:
        with open(f'files/{minus_file}', 'wb') as file_minus:  # строка, где указываем путь к папке
            file_minus.write(resp.content)
    except Exception as ex:
        print(f'Ошибка {link}: {ex}')
    return f'{minus_file}'


def get_items(url: str, x: int) -> list:  # получаем необходимые элементы
    amount = 1
    soup_song = cooking_soup(url)
    html_code = '-'
    h1 = soup_song.find('h1').text.strip()
    title = soup_song.find('title').text.strip(' =-')
    description = soup_song.find('meta', {'name': 'keywords'})['content']
    categories = soup_song.find('div', class_='tags-block hidden-on-mobile')
    if categories.text.isspace():
        categories = '-'
    else:
        categories = ''.join(list(map(lambda i: i.text + '\n', categories.find_all('a', class_='tag'))))
    lyrics = soup_song.find('div', class_='tabs-block__container')
    if lyrics:
        html_code = lyrics
        lyrics = lyrics.text.strip()
    video = soup_song.find('div', class_='track-tabs__video')
    if video:
        video = video.find('iframe')['src']
    minus = soup_song.find('div', class_='track-tabs__instrumentals')
    if minus:
        minus = get_minus(minus, x)
        amount += 1
    a = soup_song.find('a', class_='player__download download hidden-on-mobile')['href']
    audio_file = a.split("/")[-1].strip('.mp3')
    if audio_file == '':
        audio_file = h1 + f'_{x}.mp3'
    else:
        audio_file += f'_{x}.mp3'
    song = 'https://xn----9sbmabsiicuddu3a5lep.xn--p1ai' + a
    resp = rq.get(song)
    try:
        with open(f'files/{audio_file}', 'wb') as file_song:  # строка, где указываем путь к папке
            file_song.write(resp.content)
            amount += 1
    except Exception as ex:
        print(h1, f'Страница: {page}')
    return list(map(lambda x: '-' if x is None else x,
                    [url, h1, title, description, lyrics, html_code, amount, audio_file, minus, video, categories]))


head = ['URL', 'Название', 'Полное название', 'Описание', 'Текст песни', 'HTML код текста', 'Количество файлов', 'Файлы аудио',
        'Файлы минусовок', 'Видео', 'Категории']


with open('list_of_songs.csv', 'a', encoding='utf-8-sig', newline='') as file_csv:  # строка, где указываем название csv файла и записываем шапку
    writer = csv.writer(file_csv, delimiter=';')
    writer.writerow(head)


x = 1
for page in range(1, 39):  # перебираем страницы с песнями
    try:
        soup = cooking_soup(f'https://xn----9sbmabsiicuddu3a5lep.xn--p1ai/kolybelnye?page={page}')
        with open('list_of_songs.csv', 'a', encoding='utf-8-sig', newline='') as file_csv:  # строка, где указываем название csv файла
            writer = csv.writer(file_csv, delimiter=';')
            for page_song in soup.find_all('a', class_='player__track-name player__track-name-init'):  # перебираем страницы песен
                url = 'https://xn----9sbmabsiicuddu3a5lep.xn--p1ai' + page_song['href']
                writer.writerow(get_items(url, x))
                x += 1
        print(f'Процесс на странице {page} завершен.')
    except Exception as ex:
        print(f'Ошибка на странице {page}: {ex}')
