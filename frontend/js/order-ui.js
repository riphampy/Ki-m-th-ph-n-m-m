import { api } from './api.js';
import { $, user, esc, money, date, statusBadge, action, confirmDialog, toast } from './ui.js';
export function orderButtons(order) {
  if(user.role==='CUSTOMER') return order.status==='PENDING'?`<button class="danger small" type="button" data-cancel="${order.id}" data-testid="order-cancel-button-${order.id}">Hủy đơn</button>`:'';
  const next={PENDING:['CONFIRMED','confirm','Xác nhận'],CONFIRMED:['SHIPPING','ship','Giao hàng'],SHIPPING:['COMPLETED','complete','Hoàn thành']}[order.status];
  return `${next?`<button class="small" type="button" data-transition="${next[0]}" data-order="${order.id}" data-testid="admin-order-${next[1]}-button-${order.id}">${next[2]}</button>`:''}${['PENDING','CONFIRMED'].includes(order.status)?`<button class="danger small" type="button" data-cancel="${order.id}" data-testid="admin-order-cancel-button-${order.id}">Hủy đơn</button>`:''}`;
}
export function orderTable(orders) {
  return `<div class="table-wrap"><table><thead><tr><th>Đơn hàng</th><th>Ngày đặt</th>${user.role==='ADMIN'?'<th>Người nhận</th>':''}<th>Tổng tiền</th><th>Trạng thái</th><th>Thao tác</th></tr></thead><tbody>${orders.map(order=>`<tr data-testid="order-row-${order.id}"><td><a href="/order-detail.html?id=${order.id}" data-testid="order-detail-link-${order.id}">#${order.id}</a></td><td data-testid="order-date-${order.id}">${date(order.created_at)}</td>${user.role==='ADMIN'?`<td>${esc(order.recipient_name)}</td>`:''}<td class="amount" data-testid="order-total-amount-${order.id}">${money(order.total)}</td><td>${statusBadge(order)}</td><td><div class="actions">${orderButtons(order)}</div></td></tr>`).join('')}</tbody></table></div>`;
}
export function bindOrderActions(root, refresh) {
  root.querySelectorAll('[data-cancel]').forEach(button=>{button.onclick=()=>action(button,async()=>{
    if(!await confirmDialog(`Hủy đơn hàng #${button.dataset.cancel}?`))return;
    const result=await api(`/orders/${button.dataset.cancel}/cancel`,{method:'PUT'});await refresh();toast(result.message);
  });});
  root.querySelectorAll('[data-transition]').forEach(button=>{button.onclick=()=>action(button,async()=>{
    const result=await api(`/admin/orders/${button.dataset.order}/status`,{method:'PUT',body:{status:button.dataset.transition}});await refresh();toast(result.message);
  });});
}
export function itemTable(order) {
  return `<div class="table-wrap"><table><thead><tr><th>Sản phẩm</th><th>Đơn giá</th><th>Số lượng</th><th>Thành tiền</th></tr></thead><tbody>${order.items.map(item=>`<tr data-testid="order-detail-item-${item.product_id}"><td>${esc(item.product_name)}</td><td class="amount" data-testid="order-detail-price-${item.product_id}">${money(item.unit_price)}</td><td data-testid="order-detail-quantity-${item.product_id}">${item.quantity}</td><td class="amount" data-testid="order-detail-subtotal-${item.product_id}">${money(item.subtotal)}</td></tr>`).join('')}</tbody></table></div>`;
}
