import time
from selenium import webdriver
import csv
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter


def write_to_csv(data: list):
    with open("movies.csv", "w", newline="") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerows(data)


def parse_html(data: str):
    data_text = ["; ".join(li.stripped_strings) for li in data]
    parsed_data = [row.split("; ") for row in data_text]

    return parsed_data


def get_page_html():
    chrome_service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=chrome_service)
    driver.get("https://www.imdb.com/chart/top")
    layout_button = driver.find_element(By.ID, "list-view-option-detailed")
    layout_button.click()
    prev_count = 0
    while True:
        driver.execute_script(
            "window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(1)

        items = driver.find_elements(
            By.CSS_SELECTOR,
            "ipc-metadata-list ipc-metadata-list--dividers-between sc-748571c8-0 gFCVNT detailed-list-view ipc-metadata-list--base")  
        current_count = len(items)

        if current_count == prev_count:
            break
        prev_count = current_count

    html = driver.page_source
    driver.quit()

    return html


def prepare_data(data: list[list]):
    result = []

    for item in data:
        filtered_item = [
            item[0],  # Título
            item[1],  # Ano
            item[2],  # Hora
            item[3] if len(item) < 14 else item[4],  # Nota
            item[6] if len(item) < 14 else item[7],  # Descrição (ajustado, caso necessário)
            item[8] if len(item) < 14 else item[9],  # Diretor
            item[10] if len(item) > 14 else item[11] if len(item) > 11 else "",  # Ator
        ]
        result.append(filtered_item)

    return result


def count_actor(movies_data: list):
    actor_counter = Counter()
    for movie in movies_data:
        actor = movie[6] 
        if actor:
            actor_list = actor.split(";")
            for actor in actor_list:
                actor_counter[actor.strip()] += 1
    return actor_counter



def count_directors(movies_data: list):
    director_counter = Counter()
    for movie in movies_data:
        directors = movie[8] 
        if directors:
            director_list = directors.split(";")
            for director in director_list:
                director_counter[director.strip()] += 1

    return director_counter


def display_menu():
    print("Escolha uma opção:")
    print("1 - Atores com mais participações nos filmes")
    print("2 - Diretores com mais participações nos filmes")
    print("3 - Filmes com maiores avaliações")
    print("4 - Sair")


def main():
    html = get_page_html()
    soup = BeautifulSoup(html, "html.parser")

    movies_html = soup.find(
        'ul',
        class_="ipc-metadata-list ipc-metadata-list--dividers-between sc-748571c8-0 gFCVNT detailed-list-view ipc-metadata-list--base")

    movies = parse_html(movies_html)
    movies = prepare_data(movies)
    write_to_csv(movies)

    # Carregar os dados do CSV
    column_names = ['Título', 'Ano', 'Hora', 'Nota', 'Descrição', 'Diretor', 'Ator']
    df = pd.read_csv('movies.csv', delimiter=';', encoding='ISO-8859-1', quotechar='"', names=column_names, header=None, on_bad_lines='skip')

    # Limpar e formatar a coluna 'Nota'
    df['Nota'] = df['Nota'].str.replace(',', '.', regex=False)  # Substituir vírgulas por pontos
    df['Nota'] = df['Nota'].str.strip()  # Remover espaços extras

    # Remover linhas com NaN na coluna 'Nota'
    df = df.dropna(subset=['Nota'])

    # Ordenar o DataFrame pela coluna 'Nota' e pegar os 10 primeiros
    top_10_filmes = df.sort_values(by='Nota', ascending=False).head(10)

    # Exibir o menu para o usuário
    while True:
        display_menu()
        choice = input("Escolha uma opção: ")
        print("\n")
        print("------------------------------------------------------------------------")


        if choice == "1":
        # Contar os atores mais aparecidos
            actor_counter = count_actor(movies)
            print("Atores com mais participações nos filmes:")
            for actor, count in actor_counter.most_common(10):  # Mostrar os 10 mais comuns
                print(f"{actor}: {count} filmes")
            print("\n")

        elif choice == "2":
            # Contar os diretores mais frequentes
            count_directors = Counter()
            for movie in movies:
                directors = movie[5] 
                if directors:
                    director_list = directors.split(";")
                    for director in director_list:
                        count_directors[director.strip()] += 1
            print("Diretores com mais participações nos filmes:")
            for director, count in count_directors.most_common(10):
                print(f"{director}: {count} filmes")
            print("\n")

        elif choice == "3":
            # Mostrar o Top 10 filmes com maiores avaliações
            print("Top 10 filmes com maiores avaliações:")
            print(top_10_filmes[['Título', 'Nota']].to_string(index=False))
            print("\n")

        elif choice == '4':
            # Sair do programa
            print("Obrigado por participar!!")
            print("\n\n")
            break

        else:
            # Opção inválida
            print("Opção inválida! Tente novamente.")
            print("\n\n")

if __name__ == "__main__":
    main()