const $ = (s, root=document) => root.querySelector(s);
const $$ = (s, root=document) => [...root.querySelectorAll(s)];
const state = { products: [], cart: new Map(), category: "All", search: "", sort: "featured", authMode: "login", user: null, wishlist: new Set() };
const money = n => "₹" + Number(n || 0).toLocaleString("en-IN", {maximumFractionDigits:0});
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

function toast(message, type="info") {
  const node = document.createElement("div");
  node.className = `toast ${type}`;
  node.innerHTML = `<span class="toast-icon">${type==="error"?"!":type==="success"?"✓":"i"}</span><span class="toast-message">${esc(message)}</span><button class="toast-close" aria-label="Dismiss notification">×</button>`;
  $(".toast-region").appendChild(node);
  $(".toast-close", node).addEventListener("click", () => node.remove());
  setTimeout(() => node.remove(), 4500);
}
async function api(url, options={}) {
  const opts = {...options, headers: {...(options.body ? {"Content-Type":"application/json"} : {}), ...(options.headers||{})}};
  const response = await fetch(url, opts);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
  return data;
}
async function loadProducts() {
  try {
    state.products = await api("/api/products");
    renderProducts();
  } catch (e) {
    $("#productGrid").innerHTML = '<div class="loading">Could not load products. Make sure the Flask server is running and refresh.</div>';
    toast(e.message, "error");
  }
}
function visibleProducts() {
  let items = state.products.filter(p => {
    const categoryOk = state.category === "All" || p.category === state.category;
    const q = state.search.trim().toLowerCase();
    const searchOk = !q || `${p.name} ${p.category} ${p.description}`.toLowerCase().includes(q);
    return categoryOk && searchOk;
  });
  if(state.sort==="price-low") items.sort((a,b)=>a.price-b.price);
  if(state.sort==="price-high") items.sort((a,b)=>b.price-a.price);
  if(state.sort==="name") items.sort((a,b)=>a.name.localeCompare(b.name));
  return items;
}
function quantityFor(id) { return state.cart.get(Number(id)) || 0; }
function renderProducts() {
  const items = visibleProducts();
  $("#productsHeading").innerHTML = state.search ? `Search results<span>.</span>` : state.category==="All" ? `Trending right now<span>.</span>` : `${esc(state.category)}<span>.</span>`;
  $("#resultsMessage").textContent = state.search ? `${items.length} match${items.length===1?"":"es"} for “${state.search}”` : "Fresh picks for your everyday.";
  $("#emptyState").classList.toggle("hidden", items.length > 0);
  $("#productGrid").classList.toggle("hidden", items.length === 0);
  $("#productGrid").innerHTML = items.map(p => {
    const qty = quantityFor(p.id), saved = state.wishlist.has(p.id);
    return `<article class="product-card">
      <div class="product-image"><span class="product-tag">${p.featured ? "Plugd pick" : esc(p.category)}</span><button class="wish-toggle ${saved?"saved":""}" data-wish="${p.id}" aria-label="${saved?"Remove from":"Add to"} wishlist">${saved?"♥":"♡"}</button><img loading="lazy" src="${esc(p.image)}" alt="${esc(p.name)}" onerror="this.style.opacity='.15'"></div>
      <div class="product-info"><div class="product-category">${esc(p.category)}</div><div class="product-name">${esc(p.name)}</div><div class="product-desc">${esc(p.description)}</div>
      <div class="product-bottom"><div class="price">${money(p.price)} <small>INR</small></div>
      ${qty ? `<div class="quantity-control" aria-label="Quantity"><button data-qty="${p.id}" data-delta="-1" aria-label="Decrease quantity">−</button><span>${qty}</span><button data-qty="${p.id}" data-delta="1" aria-label="Increase quantity">+</button></div>` : `<button class="add-button" data-add="${p.id}" aria-label="Add ${esc(p.name)} to cart">+</button>`}
      </div></div></article>`;
  }).join("");
  updateCartCount();
}
function updateCartCount() {
  const count = [...state.cart.values()].reduce((a,b)=>a+b,0);
  $("#cartCount").textContent = count;
  $("#cartTitleCount").textContent = count ? `(${count})` : "";
}
async function syncCartFromServer() {
  if (!state.user) return;
  try {
    const data = await api("/api/cart");
    state.cart = new Map(data.items.map(i=>[Number(i.product_id), Number(i.quantity)]));
    renderProducts();
  } catch(e) { toast(e.message,"error"); }
}
async function changeQuantity(id, delta) {
  const product = state.products.find(p=>Number(p.id)===Number(id));
  if(!product) return;
  const old = quantityFor(id), next = old + delta;
  if(next > product.stock) { toast("Not enough stock available.", "error"); return; }
  if(next <= 0) state.cart.delete(Number(id)); else state.cart.set(Number(id), next);
  renderProducts();
  if(state.user) {
    try {
      await api(`/api/cart/items/${id}`, {method:"PUT", body:JSON.stringify({quantity:next})});
    } catch(e) { toast(e.message,"error"); await syncCartFromServer(); }
  }
  if(!$("#cartDrawer").classList.contains("hidden")) renderCart();
}
async function addToCart(id) {
  if(!state.user) {
    const current = quantityFor(id);
    state.cart.set(Number(id), current+1);
    renderProducts();
    toast("Added to your demo cart. Sign in to save it to your account.", "success");
    return;
  }
  try {
    await api("/api/cart/items", {method:"POST",body:JSON.stringify({product_id:Number(id),quantity:1})});
    state.cart.set(Number(id), quantityFor(id)+1);
    renderProducts();
    toast("Added to cart.", "success");
  } catch(e) { toast(e.message,"error"); }
}
function openOverlay() { $("#overlay").classList.remove("hidden"); }
function closeAll() {
  $("#overlay").classList.add("hidden");
  $("#cartDrawer").classList.add("hidden");
  $("#authModal").classList.add("hidden");
  $("#checkoutModal").classList.add("hidden");
}
function openCart() { closeAll(); openOverlay(); $("#cartDrawer").classList.remove("hidden"); renderCart(); }
function openAuth() { closeAll(); openOverlay(); $("#authModal").classList.remove("hidden"); }
function renderCart() {
  const items = [...state.cart.entries()].map(([id,quantity])=> {
    const p = state.products.find(x=>Number(x.id)===Number(id));
    return p ? {...p,quantity} : null;
  }).filter(Boolean);
  const total = items.reduce((sum,p)=>sum+p.price*p.quantity,0);
  $("#cartItems").innerHTML = items.length ? items.map(p=>`<div class="cart-item">
    <div class="cart-item-image"><img src="${esc(p.image)}" alt="${esc(p.name)}"></div>
    <div><div class="cart-item-name">${esc(p.name)}</div><div class="cart-item-meta">${esc(p.category)}</div><div class="cart-item-price">${money(p.price)}</div></div>
    <div class="cart-qty"><button data-cart-qty="${p.id}" data-delta="-1" aria-label="Decrease ${esc(p.name)}">−</button><span>${p.quantity}</span><button data-cart-qty="${p.id}" data-delta="1" aria-label="Increase ${esc(p.name)}">+</button></div>
  </div>`).join("") : '<div class="cart-empty"><strong>Your cart is waiting.</strong>Add something you love and it will show up here.</div>';
  $("#itemsTotal").textContent = money(total);
  $("#grandTotal").textContent = money(total+2);
  $("#stickyTotal").textContent = money(total+2);
  $("#cartTitleCount").textContent = items.length ? `(${items.reduce((s,p)=>s+p.quantity,0)})` : "";
  $("#checkoutButton").innerHTML = `${state.user?"Proceed to checkout":"Login to Proceed"} <span>›</span>`;
}
async function toggleWishlist(id) {
  if(!state.user) { toast("Sign in to save wishlist items.", "info"); openAuth(); return; }
  try {
    const data = await api(`/api/wishlist/${id}`, {method:"POST"});
    if(data.saved) state.wishlist.add(Number(id)); else state.wishlist.delete(Number(id));
    renderProducts();
    toast(data.saved?"Added to wishlist.":"Removed from wishlist.", "success");
  } catch(e) { toast(e.message,"error"); }
}
function setAuthMode(mode) {
  state.authMode = mode;
  $$(".auth-tab").forEach(b=>b.classList.toggle("active",b.dataset.mode===mode));
  $("#nameField").classList.toggle("hidden",mode!=="register");
  $('input[name="name"]').required = mode==="register";
  $("#authTitle").textContent = mode==="login" ? "Good to have you." : "Let’s get you plugged in.";
  $("#authSubmit").innerHTML = `${mode==="login"?"Sign in":"Create account"} <span>↗</span>`;
}
async function submitAuth(event) {
  event.preventDefault();
  const form = new FormData($("#authForm"));
  const body = Object.fromEntries(form.entries());
  try {
    const data = await api(state.authMode==="login"?"/api/login":"/api/register", {method:"POST",body:JSON.stringify(body)});
    state.user = data.user;
    closeAll();
    toast(data.message || "You're signed in.", "success");
    await syncCartFromServer();
  } catch(e) {
    // Toast lives at z-index 200, above the overlay and modal, so errors remain readable.
    toast(e.message, "error");
  }
}
async function loadUser() {
  try {
    const data = await api("/api/me");
    state.user = data.user;
    if(state.user) {
      const cart = await api("/api/cart");
      state.cart = new Map(cart.items.map(i=>[Number(i.product_id),Number(i.quantity)]));
      const wish = await api("/api/wishlist");
      state.wishlist = new Set(wish.items.map(i=>Number(i.id)));
      renderProducts();
    }
  } catch(e) { /* Anonymous browsing is supported. */ }
}
$("#searchInput").addEventListener("input", e => {
  // Intentionally do not scroll or focus another element while typing. The sticky search/header
  // stays fixed; only the product results below update, avoiding the old per-keystroke jump.
  state.search = e.target.value;
  renderProducts();
});
$("#sortSelect").addEventListener("change",e=>{state.sort=e.target.value;renderProducts()});
$(".category-nav").addEventListener("click",e=>{
  const b=e.target.closest("[data-category]"); if(!b)return;
  state.category=b.dataset.category;
  $$(".category-link").forEach(x=>x.classList.toggle("active",x===b));
  renderProducts();
});
$("#productGrid").addEventListener("click",e=>{
  const add=e.target.closest("[data-add]"); if(add){addToCart(Number(add.dataset.add));return}
  const qty=e.target.closest("[data-qty]"); if(qty){changeQuantity(Number(qty.dataset.qty),Number(qty.dataset.delta));return}
  const wish=e.target.closest("[data-wish]"); if(wish)toggleWishlist(Number(wish.dataset.wish));
});
$("#cartItems").addEventListener("click",e=>{
  const b=e.target.closest("[data-cart-qty]"); if(b)changeQuantity(Number(b.dataset.cartQty),Number(b.dataset.delta));
});
$("#cartButton").addEventListener("click",openCart);
$("#closeCart").addEventListener("click",closeAll);
$("#accountButton").addEventListener("click",()=>state.user ? toast(`Signed in as ${state.user.name}.`, "success") : openAuth());
$("#closeAuth").addEventListener("click",closeAll);
$("#closeCheckout").addEventListener("click",closeAll);
$("#overlay").addEventListener("click",closeAll);
$("#authForm").addEventListener("submit",submitAuth);
$$(".auth-tab").forEach(b=>b.addEventListener("click",()=>setAuthMode(b.dataset.mode)));
$("#shopNow").addEventListener("click",()=>$("#productsSection").scrollIntoView({behavior:"smooth",block:"start"}));
$("#clearSearch").addEventListener("click",()=>{$("#searchInput").value="";state.search="";state.category="All";$$(".category-link").forEach(x=>x.classList.toggle("active",x.dataset.category==="All"));renderProducts()});
$("#shareCart").addEventListener("click",async()=>{try{await navigator.clipboard.writeText(location.href);toast("Store link copied.", "success")}catch(e){toast("Copy this page address to share the store.", "info")}});
$("#checkoutButton").addEventListener("click",()=>{
  if(!state.cart.size){toast("Your cart is empty.", "info");return}
  if(!state.user){openAuth();return}
  closeAll();openOverlay();$("#checkoutModal").classList.remove("hidden");
});
$("#checkoutForm").addEventListener("submit",async e=>{
  e.preventDefault();
  try {
    const data=await api("/api/orders",{method:"POST",body:JSON.stringify({shipping_address:new FormData(e.currentTarget).get("shipping_address")})});
    state.cart.clear();closeAll();renderProducts();toast(`Demo order #${data.order_id} placed. Total ${money(data.total)}.`, "success");
  } catch(err){toast(err.message,"error")}
});
$("#wishlistButton").addEventListener("click",()=>{if(!state.user){openAuth();return}const saved=state.products.filter(p=>state.wishlist.has(Number(p.id)));toast(saved.length?`Wishlist: ${saved.map(p=>p.name).join(", ")}`:"Your wishlist is empty.", "info")});
document.addEventListener("keydown",e=>{if(e.key==="Escape")closeAll();if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==="k"){e.preventDefault();$("#searchInput").focus()}});
(async()=>{await loadProducts();await loadUser();})();
