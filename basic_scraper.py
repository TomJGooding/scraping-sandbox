import dataclasses
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/catalogue/"

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


@dataclasses.dataclass
class Book:
    title: str
    price: float
    rating: int


def scrape_books() -> list[Book]:
    books: list[Book] = []

    page_number = 1

    while True:
        url = f"{BASE_URL}page-{page_number}.html"
        response = requests.get(url)

        soup = BeautifulSoup(response.content, "html.parser")
        book_containers = soup.find_all("article", class_="product_pod")

        for book_container in book_containers:
            book_title = book_container.select_one("h3 a").get("title")
            price_text = book_container.select_one("p.price_color").get_text()
            price = float(price_text[1:])
            star_rating = book_container.select_one("p.star-rating")
            rating_class = star_rating["class"][1]
            rating = RATING_MAP[rating_class]

            books.append(Book(book_title, price, rating))

        next_page = soup.select_one("li.next a")
        if next_page is not None:
            page_number += 1
        else:
            break

    return books


if __name__ == "__main__":
    start_time = time.time()
    books = scrape_books()
    end_time = time.time()
    print(f"Scraped {len(books)} books in {end_time - start_time:.2f} seconds")

    books_df = pd.DataFrame(dataclasses.asdict(book) for book in books)
    print(books_df)
