# Plugd — Electronics Store Demo

A beginner-friendly Flask + SQLite electronics storefront.

## Run on WSL / Ubuntu

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip -y
cd ~/projects/plugd/plugd-store
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
- Server-side cart, wishlist, demo checkout, and order history endpoints
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
- `GET /api/wishlist`
- `POST /api/wishlist/<product_id>` (toggle)
- `POST /api/orders`
- `GET /api/orders`

## Notes

- This is a student/demo project, not a production commerce service.
- Checkout creates a demo order; no real payment gateway is connected.
- The user interface allows a temporary cart before sign-in. Server-side cart persistence is available after sign-in.
- Before deployment, replace `app.secret_key` with a secure environment variable, configure HTTPS, add CSRF protection/rate limiting, and build a proper admin role/dashboard.
- Product images are loaded from Unsplash and require internet access.
