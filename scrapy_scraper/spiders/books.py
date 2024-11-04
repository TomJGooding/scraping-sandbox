import scrapy

from scrapy_scraper.items import BookItem


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
        books = response.css("article.product_pod")
        for book in books:
            book_item = BookItem()
            book_item["title"] = book.css("h3 a").attrib["title"]
            book_item["price"] = book.css("p.price_color ::text").get()
            book_item["rating"] = book.css("p.star-rating").attrib["class"]
            yield book_item

        next_page = response.css("li.next a ::attr(href)").get()
        if next_page is not None:
            if "catalogue" in next_page:
                next_page_url = "https://books.toscrape.com/" + next_page
            else:
                next_page_url = "https://books.toscrape.com/catalogue/" + next_page

            yield response.follow(next_page_url, callback=self.parse)
