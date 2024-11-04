from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class BooksPipeline:
    rating_map = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if not adapter.get("title"):
            raise DropItem(f"Missing title in {item}")

        price_string = adapter.get("price")
        if price_string:
            price_string = price_string.replace("£", "")
            adapter["price"] = float(price_string)
        else:
            raise DropItem(f"Missing price in {item}")

        rating_classes = adapter.get("rating", default="")
        try:
            rating_string = rating_classes.split()[1]
            adapter["rating"] = self.rating_map.get(rating_string)
        except (IndexError, KeyError):
            raise DropItem(f"Missing or invalid rating in {item}")

        return item
