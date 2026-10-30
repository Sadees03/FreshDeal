
from flask import Flask, render_template, request, redirect, url_for
import json
from pathlib import Path
from datetime import date

app = Flask(__name__)

DATA_FILE = Path(__file__).parent / "products.json"


def load_products():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return []


@app.route("/")
def home():
    products = load_products()
    today = date.today()

    total_products = len(products)
    total_units = sum(p["quantity"] for p in products)
    inventory_value = sum(
        p["price"] * p["quantity"] for p in products
    )

    for product in products:
        expiry = date.fromisoformat(product["expiry"])
        product["days_left"] = (expiry - today).days

    expired = sum(
        1 for p in products if p["days_left"] < 0
    )

    urgent = sum(
        1 for p in products if 0 <= p["days_left"] <= 3
    )

    return render_template(
        "index.html",
        products=products,
        total_products=total_products,
        total_units=total_units,
        inventory_value=inventory_value,
        expired=expired,
        urgent=urgent
    )
@app.route("/add", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        products = load_products()

        next_id = max(
            (p.get("id", 0) for p in products),
            default=0
        ) + 1

        product = {
            "name": request.form["name"],
            "category": request.form["category"],
            "price": float(request.form["price"]),
            "quantity": int(request.form["quantity"]),
            "expiry": request.form["expiry"]
        }

        products.append(product)

        with open(DATA_FILE, "w") as file:
            json.dump(products, file, indent=4)

        return redirect(url_for("home"))

    return render_template("add.html")

@app.route("/search", methods=["GET", "POST"])
def search_product():
    results = []
    searched = False

    if request.method == "POST":
        searched = True
        search_name = request.form.get("name", "").strip().lower()
        products = load_products()

        results = [
            product for product in products
            if search_name in product["name"].lower()
        ]

    return render_template(
        "search.html",
        results=results,
        searched=searched
    )


if __name__ == "__main__":
    app.run(debug=True)
