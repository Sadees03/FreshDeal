
import json
import csv
from datetime import date, datetime, timedelta
from pathlib import Path

DATA_FILE = Path("products.json")


def load_products():
    """Load saved products from the JSON file."""
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            print("Warning: Invalid inventory format. Starting empty.")
            return []

        return data

    except (json.JSONDecodeError, OSError):
        print("Warning: Could not read inventory. Starting empty.")
        return []


def save_products(products):
    """Save the current inventory to the JSON file."""
    try:
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(products, file, indent=4)
        return True
    except OSError:
        print("Error: Could not save inventory.")
        return False


def get_expiry_date():
    """Ask for an expiry date in YYYY-MM-DD format."""
    while True:
        value = input("Expiry date (YYYY-MM-DD): ").strip()

        try:
            return date.fromisoformat(value)
        except ValueError:
            print("Invalid date. Example: 2026-12-31")


def add_product(products):
    """Add a product to the inventory."""
    print("\n--- ADD NEW PRODUCT ---")

    name = input("Product name: ").strip().title()
    category = input("Category: ").strip().title()

    if not name or not category:
        print("Name and category cannot be empty.")
        return

    try:
        price = float(input("Price per unit (Rs.): "))
        quantity = int(input("Quantity: "))

        if price <= 0 or quantity <= 0:
            print("Price and quantity must be positive.")
            return

    except ValueError:
        print("Enter a valid price and whole-number quantity.")
        return

    expiry = get_expiry_date()

    next_id = max(
        (product["id"] for product in products),
        default=0
    ) + 1

    product = {
        "id": next_id,
        "name": name,
        "category": category,
        "price": round(price, 2),
        "quantity": quantity,
        "expiry": expiry.isoformat()
    }

    products.append(product)

    if save_products(products):
        print(f"{name} added successfully. Product ID: {next_id}")
    else:
        products.pop()


def view_products(products):
    """Display all inventory products."""
    print("\n--- CURRENT INVENTORY ---")

    if not products:
        print("No products found.")
        return

    print(
        f"{'ID':<5}{'Product':<20}{'Category':<15}"
        f"{'Price':>10}{'Qty':>7}  {'Expiry':<12}"
    )
    print("-" * 72)

    for product in products:
        print(
            f"{product['id']:<5}"
            f"{product['name']:<20}"
            f"{product['category']:<15}"
            f"{product['price']:>10.2f}"
            f"{product['quantity']:>7}  "
            f"{product['expiry']:<12}"
        )


def get_days_left(product):
    """Calculate the number of days until expiry."""
    expiry = date.fromisoformat(product["expiry"])
    return (expiry - date.today()).days


def expiry_report(products):
    """Show expired and soon-to-expire products."""
    print("\n--- EXPIRY ALERT REPORT ---")

    if not products:
        print("No products available.")
        return

    expired = []
    urgent = []
    upcoming = []
    safe = []

    for product in products:
        days_left = get_days_left(product)

        if days_left < 0:
            expired.append(product)
        elif days_left <= 3:
            urgent.append(product)
        elif days_left <= 7:
            upcoming.append(product)
        else:
            safe.append(product)

    def display_group(title, items):
        print(f"\n{title} ({len(items)} products)")

        if not items:
            print("  None")
            return

        for item in items:
            days = get_days_left(item)

            if days < 0:
                status = f"Expired {-days} day(s) ago"
            elif days == 0:
                status = "Expires today"
            else:
                status = f"{days} day(s) left"

            print(
                f"  ID {item['id']} | {item['name']} | "
                f"Qty: {item['quantity']} | {status}"
            )

    display_group("EXPIRED - DO NOT SELL", expired)
    display_group("URGENT - 0 TO 3 DAYS", urgent)
    display_group("UPCOMING - 4 TO 7 DAYS", upcoming)
    display_group("NO IMMEDIATE ALERT", safe)


def simulate_discount(products):
    """Calculate a discount without changing actual inventory prices."""
    print("\n--- DISCOUNT SIMULATOR ---")

    try:
        product_id = int(input("Enter product ID: "))
        discount_percent = float(
            input("Discount percentage (0-100): ")
        )

    except ValueError:
        print("Enter a valid ID and percentage.")
        return

    product = next(
        (item for item in products if item["id"] == product_id),
        None
    )

    if product is None:
        print("Product not found.")
        return

    if not 0 <= discount_percent <= 100:
        print("Discount must be between 0 and 100.")
        return

    days_left = get_days_left(product)

    if days_left < 0:
        print("This product is expired. It cannot be discounted for sale.")
        return

    if product["quantity"] <= 0:
        print("This product is out of stock.")
        return

    original_price = product["price"]
    discounted_price = original_price * (
        1 - discount_percent / 100
    )

    original_revenue = original_price * product["quantity"]
    potential_revenue = discounted_price * product["quantity"]
    revenue_difference = original_revenue - potential_revenue

    print("\n--- SIMULATION RESULT ---")
    print("Product:", product["name"])
    print("Days until expiry:", days_left)
    print(f"Original unit price: Rs. {original_price:.2f}")
    print(f"Discount: {discount_percent:.1f}%")
    print(f"Discounted unit price: Rs. {discounted_price:.2f}")
    print(f"Quantity available: {product['quantity']}")
    print(f"Original stock value: Rs. {original_revenue:.2f}")
    print(f"Potential revenue if all sell: Rs. {potential_revenue:.2f}")
    print(f"Revenue difference: Rs. {revenue_difference:.2f}")

    print("\nNote: This is a simulation, not a sales prediction.")
    print("Actual demand and unsold stock may differ.")


    
def search_product(products):
    keyword = input("Enter product name to search: ").strip().lower()

    matches = [
        item for item in products
        if keyword in item["name"].lower()
    ]

    if not matches:
        print("No matching products found.")
        return

    print("\n--- SEARCH RESULTS ---")

    for item in matches:
        days_left = get_days_left(item)

        print(
            f"ID: {item['id']} | "
            f"{item['name']} | "
            f"Price: Rs. {item['price']:.2f} | "
            f"Quantity: {item['quantity']} | "
            f"Days until expiry: {days_left}"
        )

def restock_product(products):
    try:
        product_id = int(input("Enter product ID to restock: "))
        quantity = int(input("Quantity to add: "))

        if quantity <= 0:
            print("Quantity must be positive.")
            return

    except ValueError:
        print("Enter valid whole numbers.")
        return

    product = next(
        (item for item in products if item["id"] == product_id),
        None
    )

    if product is None:
        print("Product not found.")
        return

    product["quantity"] += quantity

    if save_products(products):
        print(
            f"Stock updated. New quantity: {product['quantity']}"
        )
    else:
        product["quantity"] -= quantity


    
def export_inventory(products):
    if not products:
        print("No products available to export.")
        return

    try:
        with open(
            "inventory_report.csv",
            "w",
            newline="",
            encoding="utf-8"
        ) as file:
            fields = [
                "id", "name", "category",
                "price", "quantity", "expiry"
            ]

            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            writer.writerows(products)

        print("Inventory exported to inventory_report.csv")

    except OSError:
        print("Could not export the inventory report.")





def inventory_summary(products):
    """Display basic inventory statistics."""
    total_products = len(products)
    total_units = sum(item["quantity"] for item in products)
    total_value = sum(
        item["price"] * item["quantity"] for item in products
    )

    expired_count = sum(
        1 for item in products if get_days_left(item) < 0
    )

    urgent_count = sum(
        1 for item in products
        if 0 <= get_days_left(item) <= 3
    )

    print("\n--- INVENTORY SUMMARY ---")
    print("Different products:", total_products)
    print("Total units in stock:", total_units)
    print(f"Total inventory value: Rs. {total_value:.2f}")
    print("Expired product types:", expired_count)
    print("Products expiring within 3 days:", urgent_count)


def main():
    products = load_products()

    while True:
        print("\n" + "=" * 38)
        print("       FRESHDEAL MANAGER")
        print("=" * 38)
        print("1. Add product")
        print("2. View inventory")
        print("3. Expiry alert report")
        print("4. Simulate a discount")
        print("5. Inventory summary")
        print("6. Search for a product")
        print("7. Restock a product")
        print("8. Export inventory to CSV")
        print("9. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            add_product(products)
        elif choice == "2":
            view_products(products)
        elif choice == "3":
            expiry_report(products)
        elif choice == "4":
            simulate_discount(products)
        elif choice == "5":
            inventory_summary(products)
        elif choice == "6":
            search_product(products)
        elif choice == "7":
            restock_product(products)
        elif choice == "8":
            export_inventory(products)
        elif choice == "9":
            print("Thank you for using FreshDeal!")
            break

if __name__ == "__main__":
    main()