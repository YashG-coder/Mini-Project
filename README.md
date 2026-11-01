# Plugd — Electronics Store Demo

A beginner-friendly Flask + SQLite electronics storefront.

## Run on WSL / Ubuntu

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip -y
cd ~/projects/plugd-store-final
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in your browser. Keep the terminal open while using the site.

If the project is extracted to another location, `cd` to the folder containing `app.py` and `requirements.txt` first.

## Included

- Plugd branding and responsive storefront
- Search that filters products without scrolling the page while typing
- Sticky header/search area
- Product category filters and sorting
- Add-to-cart quantity controls (`− 1 +`)
- Cart drawer with item total, delivery, handling and grand total
- Flask JSON API and SQLite database, initialized automatically
- Account registration and login with password hashing
- Server-side cart, demo checkout, and order history endpoints
- Toast notifications rendered above the blurred overlay/modal

## API routes

- `GET /api/health`
- `GET /api/products` (optional `?search=phone&category=Phones`)
- `GET /api/products/<id>`
- `POST /api/register`
- `POST /api/login`
- `POST /api/logout`
- `GET /api/me`
- `GET /api/cart`
- `POST /api/cart/items`
- `PUT /api/cart/items/<product_id>`
- `DELETE /api/cart/items/<product_id>`
- `POST /api/orders`
- `GET /api/orders`

## Notes

- This is a student/demo project, not a production commerce service.
- Checkout creates a demo order; no real payment gateway is connected.
- The user interface allows a temporary cart before sign-in. Server-side cart persistence is available after sign-in.
- Before deployment, replace `app.secret_key` with a secure environment variable, configure HTTPS, add CSRF protection/rate limiting, and build a proper admin role/dashboard.
- Product images are loaded from Unsplash and require internet access.


## Latest requested updates
- Added five additional catalogue products in each category (Phones, Laptops, Audio, Gaming, Wearables, Accessories). New products are inserted into an existing `plugd.db` without duplicating existing rows.
- Added a My Orders view for signed-in users, including order items, total, shipping address, status, and an estimated delivery date (five days after placing the demo order).
- Added an account dropdown with Sign in/Create account and Sign out actions.
- Updated the account and cart navigation icons.

The delivery date is an estimate for this student demo; there is no live courier integration or real shipment tracking.

- Removed the wishlist feature from the storefront and API.
- Updated the ProBook 14 Laptop image to a laptop product image. Existing `plugd.db` rows are updated for this product when the app starts; other product data is preserved.
