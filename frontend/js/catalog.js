import { api, query } from './api.js';
import { $, boot, page, content, user, esc, money, date, field, formError, bindForm, values, action, toast, heading, empty, pager, art, addToCart, numberId, confirmDialog } from './ui.js';
const categories = [['','Tất cả danh mục'],[1,'CPU'],[2,'RAM'],[3,'VGA'],[4,'PSU']];
const categoryNames = {1:'CPU',2:'RAM',3:'VGA',4:'PSU'};
function productCard(product) {
  return `<article class="product-card" data-testid="product-card-${product.id}"><a class="product-art" href="/product.html?id=${product.id}" data-testid="product-card-image-link-${product.id}" aria-label="Xem ${esc(product.name)}">${art(product.category_id)}</a><div class="product-body"><div class="product-meta"><span>${esc(product.brand)}</span><span>${categoryNames[product.category_id]}</span></div><a href="/product.html?id=${product.id}" class="product-name" data-testid="product-card-name-${product.id}">${esc(product.name)}</a><div class="product-price" data-testid="product-card-price-${product.id}">${money(product.price)}</div><span class="stock ${product.stock===0?'empty':''}" data-testid="product-card-stock-${product.id}">${product.stock ? `Còn ${product.stock} sản phẩm`:'Hết hàng'}</span><button type="button" data-add="${product.id}" data-testid="product-add-to-cart-button-${product.id}" ${product.stock===0?'disabled':''}>${product.stock===0?'Hết hàng':'Thêm vào giỏ'}</button></div></article>`;
}
async function catalog() {
  const brands=(await api('/brands')).data;
  const initial=new URLSearchParams(location.search);
  content.innerHTML=`<section class="hero"><div><h1>Chọn linh kiện cho<br>cấu hình của bạn.</h1><p>Từ bộ xử lý đến bộ nguồn. Tìm linh kiện theo nhu cầu, hãng và ngân sách của bạn.</p><div class="category-strip">${categories.slice(1).map(([id,name])=>`<a href="/index.html?category_id=${id}" data-testid="home-category-link-${id}">${name}</a>`).join('')}</div></div><div class="hero-visual">${art(1)}</div></section><div class="catalog-layout"><aside class="filter-panel"><h2>Lọc sản phẩm</h2><form id="filter-form" novalidate>${formError('filter')}${field('filter','category_id','Danh mục',{options:categories,value:initial.get('category_id')||'',testid:'filter-category-select'})}${field('filter','brand','Hãng',{options:[['','Tất cả hãng'],...brands.map(b=>[b,b])],testid:'filter-brand-select'})}${field('filter','min_price','Giá từ (₫)',{type:'number',testid:'filter-min-price-input'})}${field('filter','max_price','Giá đến (₫)',{type:'number',testid:'filter-max-price-input'})}<button type="submit" data-testid="filter-apply-button">Áp dụng bộ lọc</button><button type="button" class="secondary" data-testid="filter-reset-button">Xóa bộ lọc</button></form></aside><section aria-label="Danh sách sản phẩm"><form id="search-form" class="search-row" novalidate><label class="sr-only" for="search">Tên sản phẩm</label><input id="search" name="search" placeholder="Tìm tên linh kiện…" aria-label="Tìm tên linh kiện" data-testid="search-input"><button type="submit" data-testid="search-button">Tìm kiếm</button></form><div class="catalog-toolbar"><span data-testid="home-results-count" id="result-count"></span><label for="sort" class="sr-only">Sắp xếp</label><select id="sort" data-testid="sort-select"><option value="newest">Mới nhất</option><option value="price_asc">Giá tăng dần</option><option value="price_desc">Giá giảm dần</option></select></div><div id="products" data-testid="home-products-results"></div><div id="pagination"></div></section></div>`;
  let generation=0;
  async function load(pageNumber=1) {
    const version=++generation;
    const result=await api('/products?'+query({...values($('#filter-form')),search:$('#search').value,sort:$('#sort').value,page:pageNumber}));
    if(version!==generation)return;
    const data=result.data;
    $('#result-count').textContent=`${data.total} sản phẩm`;
    $('#products').innerHTML=data.items.length?`<div class="product-grid">${data.items.map(productCard).join('')}</div>`:empty('Không tìm thấy sản phẩm phù hợp');
    $('#products').querySelectorAll('[data-add]').forEach(button=>{button.onclick=()=>action(button,()=>addToCart(Number(button.dataset.add)));});
    pager($('#pagination'),data,load);
  }
  bindForm('filter-form',()=>load()); bindForm('search-form',()=>load());
  $('#sort').onchange=()=>action($('#sort'),()=>load());
  $('[data-testid="filter-reset-button"]').onclick=event=>action(event.currentTarget,async()=>{$('#filter-form').reset();$('#filter-category_id').value='';$('#search').value='';$('#sort').value='newest';await load();});
  await load();
}
async function detail() {
  const id=numberId();
  const product=(await api(`/products/${id}`)).data;
  document.title=`${product.name} | PC Parts Shop`;
  content.innerHTML=`<p><a href="/index.html" data-testid="product-back-link">Tất cả sản phẩm</a></p><section class="detail-layout"><div class="detail-art">${art(product.category_id)}</div><div><p class="muted">${esc(product.brand)} / ${categoryNames[product.category_id]}</p><h1 data-testid="product-name-text">${esc(product.name)}</h1><p class="muted" data-testid="product-rating-value" id="average-rating">Điểm đánh giá: ${product.average_rating}/5</p><p class="detail-price" data-testid="product-price-amount">${money(product.price)}</p><p class="stock ${product.stock?'':'empty'}" data-testid="product-stock-quantity">${product.stock?`Còn ${product.stock} sản phẩm`:'Hết hàng'}</p><p class="detail-description" data-testid="product-description-text">${esc(product.description)}</p><form id="product-cart-form" novalidate>${formError('product')}${field('product','quantity','Số lượng',{type:'number',value:1,hint:'Từ 1 đến 10 sản phẩm mỗi dòng giỏ hàng.'})}<button type="submit" data-testid="product-add-to-cart-button-${id}" ${product.stock?'':'disabled'}>Thêm vào giỏ</button></form></div></section><div class="split-layout"><section class="panel"><h2>Đánh giá sản phẩm</h2><div id="reviews" data-testid="product-reviews-results"></div><div id="review-pagination"></div></section><section class="panel" id="review-compose">${user?.role==='CUSTOMER'?`<h2>Viết đánh giá</h2><p class="muted">Mỗi khách hàng được gửi một đánh giá cho sản phẩm.</p><form id="review-form" novalidate>${formError('product-review')}${reviewFields('product-review')}<button type="submit" data-testid="product-review-submit-button">Gửi đánh giá</button></form>`:!user?`<h2>Chia sẻ trải nghiệm</h2><p>Đăng nhập để viết đánh giá về sản phẩm.</p><a href="/login.html" class="button secondary" data-testid="product-review-login-link">Đăng nhập</a>`:'<h2>Quản lý đánh giá</h2><p class="muted">Bạn có thể xóa đánh giá không phù hợp trong danh sách bên cạnh.</p>'}</section></div>`;
  bindForm('product-cart-form',form=>addToCart(id,values(form,['quantity']).quantity));
  let currentPage=1;
  async function refreshRating(){const fresh=(await api(`/products/${id}`)).data;$('#average-rating').textContent=`Điểm đánh giá: ${fresh.average_rating}/5`;}
  async function loadReviews(pageNumber=1){
    currentPage=pageNumber;
    const data=(await api(`/products/${id}/reviews?page=${pageNumber}`)).data;
    if(!data.items.length && pageNumber>1){await loadReviews(pageNumber-1);return;}
    $('#reviews').innerHTML=data.items.length?data.items.map(review=>`<article class="review" data-testid="product-review-item-${review.id}"><div class="review-head"><strong>Khách hàng #${review.user_id}</strong><span class="review-rating" data-testid="product-review-rating-${review.id}">${review.rating}/5</span><span class="muted" data-testid="product-review-date-${review.id}">${date(review.created_at)}</span></div><p data-testid="product-review-comment-${review.id}">${esc(review.comment)}</p><div class="actions">${user?.id===review.user_id?`<button type="button" class="secondary small" data-edit="${review.id}" data-testid="product-review-edit-button-${review.id}">Sửa đánh giá</button>`:''}${user&&(user.id===review.user_id||user.role==='ADMIN')?`<button type="button" class="danger small" data-delete="${review.id}" data-testid="product-review-delete-button-${review.id}">Xóa đánh giá</button>`:''}</div><div id="review-edit-${review.id}"></div></article>`).join(''):empty('Chưa có đánh giá cho sản phẩm này.');
    $('#reviews').querySelectorAll('[data-edit]').forEach(button=>{button.onclick=()=>{
      const review=data.items.find(r=>r.id===Number(button.dataset.edit)); const prefix=`review-edit-${review.id}`;
      document.getElementById(prefix).innerHTML=`<form id="${prefix}-form" class="review-edit" novalidate>${formError(prefix)}${reviewFields(prefix,review)}<div class="actions"><button type="submit" data-testid="${prefix}-submit-button">Lưu đánh giá</button><button type="button" class="secondary" data-testid="${prefix}-cancel-button">Bỏ thay đổi</button></div></form>`;
      const form=bindForm(`${prefix}-form`,async form=>{const result=await api(`/reviews/${review.id}`,{method:'PUT',body:values(form,['rating'])});await loadReviews(currentPage);await refreshRating();toast(result.message);});
      $('button[type="button"]',form).onclick=()=>{document.getElementById(prefix).innerHTML='';button.focus();};
      $('select',form).focus();
    };});
    $('#reviews').querySelectorAll('[data-delete]').forEach(button=>{button.onclick=()=>action(button,async()=>{if(!await confirmDialog('Xóa đánh giá này?'))return;const result=await api(`/reviews/${button.dataset.delete}`,{method:'DELETE'});await loadReviews(currentPage);await refreshRating();toast(result.message);});});
    pager($('#review-pagination'),data,loadReviews,'review-pagination');
  }
  if(user?.role==='CUSTOMER')bindForm('review-form',async form=>{const result=await api(`/products/${id}/reviews`,{method:'POST',body:values(form,['rating'])});form.reset();await loadReviews();await refreshRating();toast(result.message);});
  await loadReviews();
}
function reviewFields(prefix,review={rating:5,comment:''}){return field(prefix,'rating','Điểm đánh giá',{options:[[5,'5 — Rất tốt'],[4,'4 — Tốt'],[3,'3 — Bình thường'],[2,'2 — Chưa tốt'],[1,'1 — Không hài lòng']],value:review.rating})+field(prefix,'comment','Nội dung',{type:'textarea',value:review.comment,hint:'Từ 10 đến 500 ký tự.'});}
boot(()=>page==='index'?catalog():detail());
