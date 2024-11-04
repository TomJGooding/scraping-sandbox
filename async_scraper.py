import asyncio
import dataclasses
import re
import time

import aiohttp
import pandas as pd
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


async def fetch(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url) as response:
        return await response.text()


def get_total_pages(soup: BeautifulSoup) -> int:
    pagination_element = soup.select_one("ul.pager li.current")
    if pagination_element:
        pagination_text = pagination_element.get_text(strip=True)
        match = re.search(r"Page \d+ of (\d+)", pagination_text)
        if match:
            return int(match.group(1))
    return 1


def parse_books(soup: BeautifulSoup) -> list[Book]:
    books: list[Book] = []

    book_containers = soup.find_all("article", class_="product_pod")

    for book_container in book_containers:
        book_title = book_container.select_one("h3 a").get("title")
        price_text = book_container.select_one("p.price_color").get_text()
        price = float(price_text[1:])
        star_rating = book_container.select_one("p.star-rating")
        rating_class = star_rating["class"][1]
        rating = RATING_MAP[rating_class]

        books.append(Book(book_title, price, rating))

    return books


async def scrape_books() -> list[Book]:
    first_page_url = f"{BASE_URL}page-1.html"
    async with aiohttp.ClientSession() as session:
        first_page_html = await fetch(session, first_page_url)
        first_page_soup = BeautifulSoup(first_page_html, "html.parser")

        total_pages = get_total_pages(first_page_soup)
        remaining_urls = [f"{BASE_URL}page-{n}.html" for n in range(2, total_pages + 1)]

        fetch_tasks = [fetch(session, url) for url in remaining_urls]
        html_contents = await asyncio.gather(*fetch_tasks)

    books: list[Book] = parse_books(first_page_soup)
    for html in html_contents:
        soup = BeautifulSoup(html, "html.parser")
        books.extend(parse_books(soup))

    return books


if __name__ == "__main__":
    start_time = time.time()
    books = asyncio.run(scrape_books())
    end_time = time.time()
    print(f"Scraped {len(books)} books in {end_time - start_time:.2f} seconds")

    books_df = pd.DataFrame(dataclasses.asdict(book) for book in books)
    print(books_df)
