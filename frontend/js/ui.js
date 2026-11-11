import { api, ApiError } from './api.js';
export const page = document.body.dataset.page;
export const $ = (selector, root = document) => root.querySelector(selector);
export const content = $('#content');
export let user = null;
export const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
export const money = value => `${new Intl.NumberFormat('vi-VN').format(value || 0)} ₫`;
export function date(value) {
  if (!value) return '—';
  const parsed = new Date(/[zZ]|[+-]\d\d:\d\d$/.test(value) ? value : value + 'Z');
  if (Number.isNaN(parsed.getTime())) return '—';
  const parts = new Intl.DateTimeFormat('vi-VN', { timeZone: 'Asia/Ho_Chi_Minh', day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }).formatToParts(parsed);
  const get = key => parts.find(p => p.type === key)?.value;
  return `${get('day')}/${get('month')}/${get('year')} ${get('hour')}:${get('minute')}`;
}
export const statuses = { PENDING: 'Chờ xác nhận', CONFIRMED: 'Đã xác nhận', SHIPPING: 'Đang giao', COMPLETED: 'Hoàn thành', CANCELLED: 'Đã hủy' };
export const statusBadge = order => `<span class="badge ${order.status.toLowerCase()}" data-testid="order-status-${order.id}">${esc(order.status_label || statuses[order.status])}</span>`;
export function toast(message, type = 'success') {
  $('#toast-text').textContent = message; $('#toast').dataset.type = type; $('#toast').hidden = false;
}
export function flash(message, type = 'success') { sessionStorage.setItem('pc-shop-flash', JSON.stringify({ message, type })); }
export function loginRedirect(message = 'Bạn cần đăng nhập để tiếp tục.') { flash(message, 'error'); location.assign('/login.html'); }
export function showError(error, form = null) {
  if (error.status === 401 && document.body.dataset.role !== 'public') { loginRedirect(error.message); return; }
  if (form) {
    const box = $('[data-form-error]', form); if (box) { box.textContent = error.message; box.hidden = false; }
    for (const [key, message] of Object.entries(error.errors || {})) {
      const field = form.elements.namedItem(key);
      if (field instanceof HTMLElement) { field.setAttribute('aria-invalid', 'true'); const target = document.getElementById(field.getAttribute('aria-describedby')); if (target) { target.textContent = message; target.hidden = false; } }
    }
  } else { $('#page-error').textContent = error.message; $('#page-error').hidden = false; }
  toast(error.message, 'error');
}
export function clearErrors(form) {
  if (form) { form.querySelectorAll('[data-form-error], .field-error').forEach(el => { el.hidden = true; el.textContent = ''; }); form.querySelectorAll('[aria-invalid]').forEach(el => el.removeAttribute('aria-invalid')); }
  $('#page-error').hidden = true;
}
export async function action(button, fn, form = null) {
  if (button?.disabled) return;
  const buttons = form ? [...form.querySelectorAll('button')] : button ? [button] : [];
  const states = buttons.map(b => b.disabled);
  buttons.forEach(b => { b.disabled = true; });
  clearErrors(form);
  try { return await fn(); } catch (error) { showError(error, form); }
  finally { buttons.forEach((b, i) => { b.disabled = states[i]; }); }
}
export function bindForm(id, fn) {
  const form = document.getElementById(id);
  form.addEventListener('submit', event => { event.preventDefault(); action($('button[type="submit"]', form), () => fn(form), form); });
  return form;
}
export function values(form, numbers = []) {
  const data = Object.fromEntries(new FormData(form));
  for (const key of numbers) if (key in data) data[key] = data[key].trim() === '' ? null : Number(data[key]);
  return data;
}
export function formError(prefix) { return `<div class="message error" data-form-error data-testid="${prefix}-error-message" role="alert" hidden></div>`; }
export function field(prefix, name, label, { type = 'text', value = '', options = null, hint = '', full = false, readonly = false, testid = '', autocomplete = '', inputmode = '' } = {}) {
  const slug = name.replaceAll('_', '-'); const id = `${prefix}-${slug}`;
  const common = `id="${id}" name="${name}" data-testid="${testid || `${id}-${options ? 'select' : type === 'textarea' ? 'textarea' : 'input'}`}" aria-describedby="${id}-error" ${readonly ? 'readonly' : ''} ${autocomplete ? `autocomplete="${autocomplete}"` : ''} ${inputmode ? `inputmode="${inputmode}"` : ''}`;
  const input = options ? `<select ${common}>${options.map(([val, text]) => `<option value="${esc(val)}" ${String(val) === String(value) ? 'selected' : ''}>${esc(text)}</option>`).join('')}</select>` : type === 'textarea' ? `<textarea ${common}>${esc(value)}</textarea>` : `<input ${common} type="${type}" value="${esc(value)}" ${type === 'number' ? 'step="1"' : ''}>`;
  return `<div class="field ${full ? 'full' : ''}"><label for="${id}">${label}</label>${input}${hint ? `<span class="hint">${hint}</span>` : ''}<p id="${id}-error" class="field-error" data-testid="${id}-error" role="alert" hidden></p></div>`;
}
export function heading(title, description = '', extra = '') { return `<div class="page-heading"><div><h1>${title}</h1>${description ? `<p>${description}</p>` : ''}</div>${extra}</div>`; }
export function empty(message, link = '') { return `<div class="empty-state" data-testid="${page}-empty-message"><p>${message}</p>${link}</div>`; }
export function pager(container, data, load, prefix = 'pagination') {
  const totalPages = Math.max(1, Math.ceil(data.total / data.page_size));
  container.innerHTML = `<div class="pagination"><button class="secondary" data-testid="${prefix}-previous-button" ${data.page <= 1 ? 'disabled' : ''}>Trang trước</button><span data-testid="${prefix}-current-page">Trang ${data.page} / ${totalPages}</span><button class="secondary" data-testid="${prefix}-next-button" ${data.page >= totalPages ? 'disabled' : ''}>Trang sau</button></div>`;
  const [previous, next] = container.querySelectorAll('button');
  previous.onclick = () => action(previous, () => load(data.page - 1));
  next.onclick = () => action(next, () => load(data.page + 1));
}
export function confirmDialog(message) {
  const dialog = $('#confirm-dialog'); $('#confirm-text').textContent = message;
  return new Promise(resolve => {
    const no = $('[data-testid="confirm-dialog-no-button"]'); const yes = $('[data-testid="confirm-dialog-yes-button"]');
    const finish = result => { dialog.close(); no.onclick = null; yes.onclick = null; dialog.oncancel = null; resolve(result); };
    no.onclick = () => finish(false); yes.onclick = () => finish(true); dialog.oncancel = event => { event.preventDefault(); finish(false); };
    dialog.showModal(); no.focus();
  });
}
export function art(category = 1) {
  const pins = Array.from({length:8}, (_,i) => `<path d="M${69+i*12} 37v12M${69+i*12} 151v12M47 ${58+i*12}h12M163 ${58+i*12}h12"/>`).join('');
  const fan = x => `<circle cx="${x}" cy="94" r="31" fill="#263e5e"/><circle cx="${x}" cy="94" r="24" fill="none" stroke="#8298b8" stroke-width="2"/><path d="M${x} 71q22 0 8 22q0 22-18 8q-22 0-8-22q0-12 18-8" fill="#7189aa"/><circle cx="${x}" cy="94" r="7" fill="#cbd9ed"/>`;
  let shapes;
  if (Number(category) === 1) shapes = `<g stroke="#8ea2be" stroke-width="5">${pins}</g><rect x="59" y="49" width="104" height="102" rx="8" fill="#426c9b"/><rect x="70" y="60" width="82" height="80" rx="5" fill="#dce7f7" stroke="#98afca"/><path d="M79 77h35M79 86h25M128 119h15" stroke="#718bac" stroke-width="3"/><text x="111" y="113" text-anchor="middle" fill="#2c527f" font-size="19" font-family="Segoe UI" font-weight="600">CPU</text>`;
  else if (Number(category) === 2) shapes = `<g transform="rotate(-14 110 100)"><rect x="20" y="64" width="190" height="65" rx="4" fill="#345d59"/><path d="M28 130h175" stroke="#bc9b4b" stroke-width="12"/>${[35,78,121,164].map(x=>`<rect x="${x}" y="77" width="30" height="35" rx="3" fill="#243b4a"/><path d="M${x+5} 83h20" stroke="#708795"/>`).join('')}<path d="M103 124v15" stroke="#edf1f7" stroke-width="6"/></g>`;
  else if (Number(category) === 3) shapes = `<path d="M17 49v105h12M29 141h158" stroke="#a0afc0" stroke-width="7"/><rect x="29" y="48" width="179" height="91" rx="8" fill="#526c89"/>${fan(77)}${fan(160)}<path d="M68 145h88" stroke="#bca267" stroke-width="8"/>`;
  else shapes = `<path d="M52 51l116-12 32 25v96L82 173l-30-29z" fill="#95a9c2"/><path d="M52 51l31 25 117-12M83 76v97" fill="none" stroke="#dce7f7" stroke-width="3"/><path d="M84 78l116-14v96L84 173z" fill="#3e5775"/><ellipse cx="142" cy="117" rx="39" ry="38" fill="#213a57"/><g fill="none" stroke="#8ba1bd" stroke-width="2"><ellipse cx="142" cy="117" rx="30" ry="29"/><ellipse cx="142" cy="117" rx="21" ry="20"/><path d="M104 117h76M142 80v74"/></g><circle cx="142" cy="117" r="9" fill="#a6b6cd"/>`;
  return `<svg viewBox="0 0 230 200" aria-hidden="true" focusable="false">${shapes}</svg>`;
}
function navigation() {
  const navLink = (href, id, label) => `<a href="${href}" data-testid="nav-${id}-link" ${location.pathname === href || (href === '/index.html' && location.pathname === '/') ? 'aria-current="page"' : ''}>${label}</a>`;
  $('#site-header').innerHTML = `<div class="header-inner"><a href="/index.html" class="brand" data-testid="nav-brand-link"><span class="brand-mark" aria-hidden="true">▦</span>PC Parts Shop</a><nav class="nav" aria-label="Điều hướng chính">${navLink('/index.html','home','Sản phẩm')}${user?.role === 'CUSTOMER' ? navLink('/cart.html','cart','Giỏ hàng') + navLink('/orders.html','orders','Đơn hàng') : ''}${user?.role === 'ADMIN' ? navLink('/admin/index.html','admin','Quản trị') : ''}<div class="user-nav">${user ? `<span class="nav-user" data-testid="nav-user-name">${esc(user.name)}</span>${navLink('/profile.html','profile','Hồ sơ')}<button class="secondary" data-testid="nav-logout-button">Đăng xuất</button>` : navLink('/login.html','login','Đăng nhập') + navLink('/register.html','register','Đăng ký')}</div></nav></div>`;
  const logout = $('[data-testid="nav-logout-button"]');
  if (logout) logout.onclick = () => action(logout, async () => { const result = await api('/auth/logout', { method: 'POST' }); flash(result.message); location.assign('/index.html'); });
  if (document.body.dataset.role === 'ADMIN' && user?.role === 'ADMIN') {
    $('.app-layout').classList.add('admin-layout'); $('#admin-nav').hidden = false;
    $('#admin-nav').innerHTML = `<h2>Quản lý cửa hàng</h2>${[['index','Tổng quan'],['products','Sản phẩm'],['inventory','Nhập kho'],['orders','Đơn hàng'],['users','Người dùng']].map(([slug,label]) => `<a href="/admin/${slug}.html" data-testid="admin-nav-${slug}-link" ${location.pathname === `/admin/${slug}.html` ? 'aria-current="page"' : ''}>${label}</a>`).join('')}`;
  }
}
export async function boot(render) {
  $('[data-testid="toast-close-button"]').onclick = () => { $('#toast').hidden = true; };
  const stored = sessionStorage.getItem('pc-shop-flash'); if (stored) { sessionStorage.removeItem('pc-shop-flash'); try { const data = JSON.parse(stored); toast(data.message, data.type); } catch {} }
  try {
    let authError;
    try { user = (await api('/auth/me')).data; } catch (error) { authError = error; if (![401,403].includes(error.status)) throw error; if (error.status === 403) toast(error.message, 'error'); }
    navigation();
    const role = document.body.dataset.role;
    if (role !== 'public' && !user) { loginRedirect(authError?.message); return; }
    if (role !== 'public' && role !== 'LOGIN' && role !== user.role) { content.innerHTML = `<section class="panel no-access"><h1 data-testid="access-denied-message">Bạn không có quyền truy cập</h1><p>Trang này chỉ dành cho ${role === 'ADMIN' ? 'quản trị viên' : 'khách hàng'}.</p><a href="/index.html" class="button" data-testid="access-denied-home-link">Về trang chủ</a></section>`; return; }
    await render();
  } catch (error) { navigation(); showError(error); }
}
export async function addToCart(productId, quantity = 1) {
  if (!user) { loginRedirect('Bạn cần đăng nhập để thêm sản phẩm vào giỏ hàng.'); return; }
  const result = await api('/cart/items', { method: 'POST', body: { product_id: productId, quantity } }); toast(result.message);
}
export function numberId() { const id = new URLSearchParams(location.search).get('id'); return /^\d+$/.test(id || '') && Number(id) > 0 ? Number(id) : 0; }
