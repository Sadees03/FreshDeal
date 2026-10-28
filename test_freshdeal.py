
import unittest
import tempfile
from pathlib import Path
from datetime import date, timedelta
from unittest.mock import patch

import main as freshdeal


class TestFreshDeal(unittest.TestCase):

    def setUp(self):
        # Create a temporary location for test data
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_file = Path(self.temp_dir.name) / "products.json"

        # Use the temporary file instead of real inventory data
        self.file_patch = patch.object(
            freshdeal, "DATA_FILE", self.test_file
        )
        self.file_patch.start()

    def tearDown(self):
        self.file_patch.stop()
        self.temp_dir.cleanup()

    def test_missing_file_returns_empty_list(self):
        products = freshdeal.load_products()
        self.assertEqual(products, [])

    def test_save_and_load_products(self):
        products = [
            {
                "id": 1,
                "name": "Milk",
                "category": "Dairy",
                "price": 50.0,
                "quantity": 20,
                "expiry": (date.today() + timedelta(days=2)).isoformat()
            }
        ]

        freshdeal.save_products(products)
        loaded_products = freshdeal.load_products()

        self.assertEqual(loaded_products, products)

    def test_days_left_for_future_expiry(self):
        product = {
            "expiry": (date.today() + timedelta(days=5)).isoformat()
        }

        result = freshdeal.get_days_left(product)

        self.assertEqual(result, 5)

    def test_days_left_for_expired_product(self):
        product = {
            "expiry": (date.today() - timedelta(days=2)).isoformat()
        }

        result = freshdeal.get_days_left(product)

        self.assertEqual(result, -2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
