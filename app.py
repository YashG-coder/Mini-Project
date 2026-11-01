from flask import Flask, jsonify, request, render_template, session
import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "plugd.db"
app = Flask(__name__)
app.secret_key = "change-this-dev-secret-before-deployment"

SAMPLE_PRODUCTS = [
    {"name":"Nova X Pro Smartphone","category":"Phones","price":69999,"description":"A powerful smartphone with a vivid display and all-day battery.","image":"https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?auto=format&fit=crop&w=800&q=80","stock":12,"featured":1},
    {"name":"AirLite Wireless Headphones","category":"Audio","price":8999,"description":"Comfortable wireless headphones with rich sound.","image":"https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80","stock":20,"featured":1},
    {"name":"ProBook 14 Laptop","category":"Laptops","price":84999,"description":"A slim laptop for study, work, and everyday creativity.","image":"https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=800&q=80","stock":8,"featured":1},
    {"name":"Pulse Smartwatch","category":"Wearables","price":12999,"description":"Track your activity and stay connected throughout the day.","image":"https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=80","stock":15,"featured":0},
    {"name":"GameBox Wireless Controller","category":"Gaming","price":5499,"description":"Responsive controls for a better gaming session.","image":"https://images.unsplash.com/photo-1600080972464-8e5f35f63d08?auto=format&fit=crop&w=800&q=80","stock":18,"featured":0},
    {"name":"USB-C Multiport Hub","category":"Accessories","price":2999,"description":"Connect your everyday devices with one compact hub.","image":"https://images.unsplash.com/photo-1625842268584-8f3296236761?auto=format&fit=crop&w=800&q=80","stock":25,"featured":0},
]
SAMPLE_PRODUCTS.extend([{'name': 'PixelEdge 9', 'category': 'Phones', 'price': 58999, 'description': 'A crisp camera system and smooth everyday performance.', 'image': 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?auto=format&fit=crop&w=800&q=80', 'stock': 10, 'featured': 0}, {'name': 'iPhone 15', 'category': 'Phones', 'price': 64999, 'description': 'Premium design with a bright display and reliable performance.', 'image': 'https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?auto=format&fit=crop&w=800&q=80', 'stock': 11, 'featured': 0}, {'name': 'Galaxy S24', 'category': 'Phones', 'price': 71999, 'description': 'A versatile flagship phone for work and entertainment.', 'image': 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=800&q=80', 'stock': 12, 'featured': 0}, {'name': 'OnePlus Nord 4', 'category': 'Phones', 'price': 29999, 'description': 'Fast, fluid performance with a vivid AMOLED display.', 'image': 'https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=800&q=80', 'stock': 13, 'featured': 0}, {'name': 'Moto Edge 50', 'category': 'Phones', 'price': 27999, 'description': 'A slim smartphone with a vibrant screen and capable camera.', 'image': 'https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?auto=format&fit=crop&w=800&q=80', 'stock': 14, 'featured': 0}, {'name': 'MacBook Air 13', 'category': 'Laptops', 'price': 99999, 'description': 'Lightweight performance for work, study, and travel.', 'image': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=800&q=80', 'stock': 15, 'featured': 0}, {'name': 'ZenBook OLED 14', 'category': 'Laptops', 'price': 92999, 'description': 'An OLED display and portable design for creators.', 'image': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=800&q=80', 'stock': 16, 'featured': 0}, {'name': 'GamingBook 15', 'category': 'Laptops', 'price': 114999, 'description': 'Dedicated graphics and fast refresh for gaming.', 'image': 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?auto=format&fit=crop&w=800&q=80', 'stock': 17, 'featured': 0}, {'name': 'IdeaPad Slim 5', 'category': 'Laptops', 'price': 67999, 'description': 'A balanced everyday laptop with a compact build.', 'image': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=800&q=80', 'stock': 18, 'featured': 0}, {'name': 'CreatorBook Pro', 'category': 'Laptops', 'price': 124999, 'description': 'A powerful workstation for demanding creative workflows.', 'image': 'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?auto=format&fit=crop&w=800&q=80', 'stock': 19, 'featured': 0}, {'name': 'StudioPods Pro', 'category': 'Audio', 'price': 12999, 'description': 'Compact earbuds with clear calls and immersive audio.', 'image': 'https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?auto=format&fit=crop&w=800&q=80', 'stock': 20, 'featured': 0}, {'name': 'SoundWave Bluetooth Speaker', 'category': 'Audio', 'price': 4999, 'description': 'Portable sound with punchy bass for every outing.', 'image': 'https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?auto=format&fit=crop&w=800&q=80', 'stock': 21, 'featured': 0}, {'name': 'QuietComfort Headset', 'category': 'Audio', 'price': 24999, 'description': 'Over-ear comfort and focused listening for long sessions.', 'image': 'https://images.unsplash.com/photo-1546435770-a3e426bf472b?auto=format&fit=crop&w=800&q=80', 'stock': 22, 'featured': 0}, {'name': 'BassBeat Earbuds', 'category': 'Audio', 'price': 3499, 'description': 'Everyday wireless earbuds with a comfortable fit.', 'image': 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=800&q=80', 'stock': 23, 'featured': 0}, {'name': 'Studio Monitor Headphones', 'category': 'Audio', 'price': 15999, 'description': 'Detailed sound for editing, mixing, and focused listening.', 'image': 'https://images.unsplash.com/photo-1484704849700-f032a568e944?auto=format&fit=crop&w=800&q=80', 'stock': 24, 'featured': 0}, {'name': 'PlayStation Console', 'category': 'Gaming', 'price': 49999, 'description': 'A powerful console for immersive next-generation gaming.', 'image': 'https://images.unsplash.com/photo-1606813907291-d86efa9b94db?auto=format&fit=crop&w=800&q=80', 'stock': 25, 'featured': 0}, {'name': 'RGB Mechanical Keyboard', 'category': 'Gaming', 'price': 6999, 'description': 'Tactile mechanical switches with customizable lighting.', 'image': 'https://images.unsplash.com/photo-1595225476474-87563907a212?auto=format&fit=crop&w=800&q=80', 'stock': 26, 'featured': 0}, {'name': 'Precision Gaming Mouse', 'category': 'Gaming', 'price': 2999, 'description': 'Lightweight design and precise tracking for competitive play.', 'image': 'https://images.unsplash.com/photo-1527814050087-3793815479db?auto=format&fit=crop&w=800&q=80', 'stock': 27, 'featured': 0}, {'name': 'Gaming Headset X', 'category': 'Gaming', 'price': 7999, 'description': 'Clear team chat and immersive positional audio.', 'image': 'https://images.unsplash.com/photo-1599669454699-248893623440?auto=format&fit=crop&w=800&q=80', 'stock': 28, 'featured': 0}, {'name': 'UltraWide Gaming Monitor', 'category': 'Gaming', 'price': 28999, 'description': 'A wide, smooth display for gaming and multitasking.', 'image': 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acd?auto=format&fit=crop&w=800&q=80', 'stock': 29, 'featured': 0}, {'name': 'FitBand Active', 'category': 'Wearables', 'price': 3999, 'description': 'A lightweight fitness band for daily activity tracking.', 'image': 'https://images.unsplash.com/photo-1557935728-e6d1eaabe558?auto=format&fit=crop&w=800&q=80', 'stock': 30, 'featured': 0}, {'name': 'Smartwatch Pro', 'category': 'Wearables', 'price': 18999, 'description': 'A bright display with useful health and fitness tools.', 'image': 'https://images.unsplash.com/photo-1434493789847-2f02dc6ca35d?auto=format&fit=crop&w=800&q=80', 'stock': 31, 'featured': 0}, {'name': 'Classic Hybrid Watch', 'category': 'Wearables', 'price': 9999, 'description': 'Classic styling with smart notifications and activity tracking.', 'image': 'https://images.unsplash.com/photo-1524805444758-089113d48a6d?auto=format&fit=crop&w=800&q=80', 'stock': 32, 'featured': 0}, {'name': 'Sport Watch Ultra', 'category': 'Wearables', 'price': 22999, 'description': 'A rugged wearable built for outdoor adventures.', 'image': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=80', 'stock': 33, 'featured': 0}, {'name': 'Everyday Smart Band', 'category': 'Wearables', 'price': 2999, 'description': 'A simple wearable for activity and sleep tracking.', 'image': 'https://images.unsplash.com/photo-1557935728-e6d1eaabe558?auto=format&fit=crop&w=800&q=80', 'stock': 34, 'featured': 0}, {'name': '65W USB-C Charger', 'category': 'Accessories', 'price': 2499, 'description': 'A compact fast charger for compatible phones and laptops.', 'image': 'https://images.unsplash.com/photo-1625842268584-8f3296236761?auto=format&fit=crop&w=800&q=80', 'stock': 35, 'featured': 0}, {'name': 'Braided USB-C Cable', 'category': 'Accessories', 'price': 799, 'description': 'A durable cable for charging and everyday connectivity.', 'image': 'https://images.unsplash.com/photo-1625842268584-8f3296236761?auto=format&fit=crop&w=800&q=80', 'stock': 36, 'featured': 0}, {'name': 'Laptop Sleeve 14', 'category': 'Accessories', 'price': 1499, 'description': 'A padded sleeve to protect your laptop on the move.', 'image': 'https://images.unsplash.com/photo-1622560480654-d96214fdc887?auto=format&fit=crop&w=800&q=80', 'stock': 37, 'featured': 0}, {'name': 'Wireless Charging Pad', 'category': 'Accessories', 'price': 1999, 'description': 'A simple charging pad for compatible devices.', 'image': 'https://images.unsplash.com/photo-1625842268584-8f3296236761?auto=format&fit=crop&w=800&q=80', 'stock': 38, 'featured': 0}, {'name': 'Adjustable Laptop Stand', 'category': 'Accessories', 'price': 1799, 'description': 'An ergonomic stand for a more comfortable desk setup.', 'image': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=800&q=80', 'stock': 39, 'featured': 0}])

def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con

def init_db():
    with connect() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT NOT NULL,
            image TEXT NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            featured INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS cart_items(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
            quantity INTEGER NOT NULL DEFAULT 1,
            UNIQUE(user_id, product_id)
        );
        CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES users(id),
            total_amount REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'Order placed',
            shipping_address TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS order_items(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
            product_id INTEGER NOT NULL REFERENCES products(id),
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL
        );
        """)
        # Keep the ProBook catalogue image focused on a laptop, including in existing databases.
        con.execute("UPDATE products SET image=? WHERE name=?", (
            "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=800&q=80",
            "ProBook 14 Laptop"
        ))
        # Insert any newly added sample products without duplicating existing catalogue rows.
        for p in SAMPLE_PRODUCTS:
            if not con.execute("SELECT id FROM products WHERE name=?", (p["name"],)).fetchone():
                con.execute("""INSERT INTO products(name,category,price,description,image,stock,featured)
                               VALUES(?,?,?,?,?,?,?)""",
                            (p["name"],p["category"],p["price"],p["description"],p["image"],p["stock"],p["featured"]))
        # Upgrade existing databases so each order has an estimated delivery date.
        columns = {r["name"] for r in con.execute("PRAGMA table_info(orders)").fetchall()}
        if "delivery_date" not in columns:
            con.execute("ALTER TABLE orders ADD COLUMN delivery_date TEXT")
        con.execute("UPDATE orders SET delivery_date=date(created_at, '+5 days') WHERE delivery_date IS NULL OR delivery_date='' ")

def current_user():
    return session.get("user_id")

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/products")
def get_products():
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()
    sql = "SELECT * FROM products WHERE 1=1"
    params = []
    if search:
        sql += " AND (name LIKE ? OR category LIKE ? OR description LIKE ?)"
        term = f"%{search}%"
        params += [term, term, term]
    if category and category.lower() != "all":
        sql += " AND category = ?"
        params.append(category)
    sql += " ORDER BY featured DESC, id DESC"
    with connect() as con:
        rows = con.execute(sql, params).fetchall()
    return jsonify([dict(row) for row in rows])

@app.get("/api/products/<int:product_id>")
def get_product(product_id):
    with connect() as con:
        row = con.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
    if not row:
        return jsonify({"error":"Product not found"}), 404
    return jsonify(dict(row))

@app.post("/api/register")
def register():
    data = request.get_json(silent=True) or request.form
    name = str(data.get("name","")).strip()
    email = str(data.get("email","")).strip().lower()
    password = str(data.get("password",""))
    if not name or not email or len(password) < 8:
        return jsonify({"error":"Enter your name and email, and use a password with at least 8 characters."}), 400
    try:
        with connect() as con:
            cur = con.execute("INSERT INTO users(name,email,password_hash) VALUES(?,?,?)",
                              (name,email,generate_password_hash(password)))
            user_id = cur.lastrowid
    except sqlite3.IntegrityError:
        return jsonify({"error":"An account with this email already exists."}), 409
    session["user_id"] = user_id
    session["user_name"] = name
    return jsonify({"message":"Account created","user":{"id":user_id,"name":name,"email":email}}), 201

@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or request.form
    email = str(data.get("email","")).strip().lower()
    password = str(data.get("password",""))
    with connect() as con:
        user = con.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error":"Invalid email or password."}), 401
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    return jsonify({"message":"Signed in successfully","user":{"id":user["id"],"name":user["name"],"email":user["email"]}})

@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"message":"Signed out"})

@app.get("/api/me")
def me():
    if not current_user():
        return jsonify({"user":None})
    return jsonify({"user":{"id":current_user(),"name":session.get("user_name")}})

def require_login():
    if not current_user():
        return jsonify({"error":"Please sign in first."}), 401
    return None

@app.get("/api/cart")
def get_cart():
    if not current_user():
        return jsonify({"items":[],"total":0})
    with connect() as con:
        rows = con.execute("""SELECT p.id AS product_id,p.name,p.price,p.image,p.stock,c.quantity
                              FROM cart_items c JOIN products p ON p.id=c.product_id
                              WHERE c.user_id=? ORDER BY c.id""", (current_user(),)).fetchall()
    items = [dict(r) for r in rows]
    return jsonify({"items":items,"total":sum(i["price"]*i["quantity"] for i in items)})

@app.post("/api/cart/items")
def add_cart_item():
    err = require_login()
    if err: return err
    data = request.get_json(silent=True) or {}
    try:
        product_id = int(data.get("product_id"))
        quantity = int(data.get("quantity",1))
    except (TypeError, ValueError):
        return jsonify({"error":"Invalid product or quantity."}), 400
    if quantity < 1:
        return jsonify({"error":"Quantity must be at least 1."}), 400
    with connect() as con:
        product = con.execute("SELECT stock FROM products WHERE id=?", (product_id,)).fetchone()
        if not product: return jsonify({"error":"Product not found."}), 404
        existing = con.execute("SELECT quantity FROM cart_items WHERE user_id=? AND product_id=?",
                                (current_user(),product_id)).fetchone()
        new_quantity = quantity + (existing["quantity"] if existing else 0)
        if new_quantity > product["stock"]:
            return jsonify({"error":"Not enough stock available."}), 400
        con.execute("""INSERT INTO cart_items(user_id,product_id,quantity) VALUES(?,?,?)
                       ON CONFLICT(user_id,product_id) DO UPDATE SET quantity=excluded.quantity""",
                    (current_user(),product_id,new_quantity))
    return get_cart()

@app.put("/api/cart/items/<int:product_id>")
def update_cart_item(product_id):
    err = require_login()
    if err: return err
    data = request.get_json(silent=True) or {}
    try: quantity = int(data.get("quantity", 0))
    except (TypeError, ValueError): return jsonify({"error":"Invalid quantity."}), 400
    with connect() as con:
        if quantity <= 0:
            con.execute("DELETE FROM cart_items WHERE user_id=? AND product_id=?", (current_user(),product_id))
        else:
            p = con.execute("SELECT stock FROM products WHERE id=?", (product_id,)).fetchone()
            if not p: return jsonify({"error":"Product not found."}), 404
            if quantity > p["stock"]: return jsonify({"error":"Not enough stock available."}), 400
            con.execute("UPDATE cart_items SET quantity=? WHERE user_id=? AND product_id=?",
                        (quantity,current_user(),product_id))
    return get_cart()

@app.delete("/api/cart/items/<int:product_id>")
def delete_cart_item(product_id):
    err = require_login()
    if err: return err
    with connect() as con:
        con.execute("DELETE FROM cart_items WHERE user_id=? AND product_id=?", (current_user(),product_id))
    return get_cart()


@app.post("/api/orders")
def create_order():
    err = require_login()
    if err: return err
    data = request.get_json(silent=True) or {}
    address = str(data.get("shipping_address","")).strip()
    if not address: return jsonify({"error":"Please enter a shipping address."}), 400
    with connect() as con:
        rows = con.execute("""SELECT p.id,p.price,p.stock,c.quantity FROM cart_items c
                              JOIN products p ON p.id=c.product_id WHERE c.user_id=?""",
                           (current_user(),)).fetchall()
        if not rows: return jsonify({"error":"Your cart is empty."}), 400
        for r in rows:
            if r["quantity"] > r["stock"]:
                return jsonify({"error":"A product no longer has enough stock."}), 400
        total = sum(r["price"]*r["quantity"] for r in rows)
        cur = con.execute("INSERT INTO orders(user_id,total_amount,shipping_address,delivery_date) VALUES(?,?,?,date('now', '+5 days'))",
                          (current_user(),total,address))
        order_id = cur.lastrowid
        for r in rows:
            con.execute("INSERT INTO order_items(order_id,product_id,quantity,unit_price) VALUES(?,?,?,?)",
                        (order_id,r["id"],r["quantity"],r["price"]))
            con.execute("UPDATE products SET stock=stock-? WHERE id=?", (r["quantity"],r["id"]))
        con.execute("DELETE FROM cart_items WHERE user_id=?", (current_user(),))
        delivery_date = con.execute("SELECT delivery_date FROM orders WHERE id=?", (order_id,)).fetchone()["delivery_date"]
    return jsonify({"message":"Demo order placed","order_id":order_id,"total":total,"delivery_date":delivery_date}), 201

@app.get("/api/orders")
def get_orders():
    err = require_login()
    if err: return err
    with connect() as con:
        rows = con.execute("SELECT * FROM orders WHERE user_id=? ORDER BY id DESC", (current_user(),)).fetchall()
        result = []
        for order in rows:
            items = con.execute("""SELECT p.name,p.image,oi.quantity,oi.unit_price
                                   FROM order_items oi JOIN products p ON p.id=oi.product_id
                                   WHERE oi.order_id=?""", (order["id"],)).fetchall()
            result.append({**dict(order), "items":[dict(item) for item in items]})
    return jsonify(result)

@app.get("/api/admin/products")
def admin_products():
    if session.get("role") != "admin":
        return jsonify({"error":"Admin access required. Admin dashboard setup is not enabled by default."}), 403
    with connect() as con:
        rows = con.execute("SELECT * FROM products ORDER BY id").fetchall()
    return jsonify([dict(r) for r in rows])

@app.get("/api/health")
def health():
    return jsonify({"status":"ok","app":"Plugd"})

init_db()

if __name__ == "__main__":
    app.run(debug=True)
