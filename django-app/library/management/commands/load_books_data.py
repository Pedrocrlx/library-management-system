import json
from django.core.management.base import BaseCommand
from library.models import Books, Categories, CategoriesPerBook
from django.db import transaction

class Command(BaseCommand):
    help = "Load books and categories from a JSON file."

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file',
            type=str,
            help='Path to the JSON file (e.g. books.json)'
        )

    @transaction.atomic
    def handle(self, *args, **kwargs):
        json_file = kwargs['json_file']

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"❌ File not found: {json_file}"))
            return
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f"❌ Invalid JSON: {e}"))
            return

        # Load categories
        self.stdout.write("➡️ Loading categories...")
        category_map = {}
        for cat in data.get("categories", []):
            obj, _ = Categories.objects.get_or_create(category_name=cat["category_name"])
            category_map[cat["id"]] = obj

        # Load books
        self.stdout.write("\n➡️ Loading books...")
        for book in data.get("books", []):
            book_obj, _ = Books.objects.get_or_create(
                book_name=book["book_name"],
                defaults={
                    "author": book["author"],
                    "quantity": book.get("quantity", 1),
                    "thumbnail": book.get("thumbnail", "")
                }
            )

            # Link categories
            for cat_id in book["categories"]:
                cat_obj = category_map.get(cat_id)
                if cat_obj:
                    CategoriesPerBook.objects.get_or_create(
                        book_id=book_obj,
                        category_id=cat_obj
                    )

        self.stdout.write(self.style.SUCCESS("\n✅ Books and categories loaded successfully!"))
