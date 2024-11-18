import time
from selenium import webdriver
import csv
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


def write_to_csv(data: list):
    with open("movies.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(data)


def parse_html(data: str):
    data_text = [", ".join(li.stripped_strings) for li in data]
    parsed_data = [row.split(", ") for row in data_text]
    return parsed_data


def prepare_data(data: list[list]):
    result = []
    for item in data:
        if '(' in item:
            item.remove('(')
        if ')' in item:
            item.remove(')')
        item.remove('Avaliar')
        result.append(item)

    return result

def get_page_html():
    chrome_service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=chrome_service)
    driver.get("https://www.imdb.com/chart/top")

    prev_count = 0
    while True:
        driver.execute_script(
            "window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(1)

        items = driver.find_elements(
            By.CSS_SELECTOR, "ul.ipc-metadata-list.ipc-metadata-list--dividers-between.sc-a1e81754-0.iyTDQy.compact-list-view.ipc-metadata-list--base > li")  # Replace with your selector
        current_count = len(items)

        if current_count == prev_count:
            break
        prev_count = current_count

    html = driver.page_source
    driver.quit()

    return html


def main():
    html = get_page_html()
    soup = BeautifulSoup(html, "html.parser")

    movies_html = soup.find(
        'ul', class_="ipc-metadata-list ipc-metadata-list--dividers-between sc-a1e81754-0 iyTDQy compact-list-view ipc-metadata-list--base")

    movies = parse_html(movies_html)
    movies = prepare_data(movies)
    write_to_csv(movies)


if __name__ == "__main__":
    main()
