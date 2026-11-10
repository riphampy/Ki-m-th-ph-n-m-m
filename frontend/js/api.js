let pending = 0;
export class ApiError extends Error {
  constructor(message, status = 0, errors = {}) { super(message); this.status = status; this.errors = errors; }
}
export async function api(path, { method = 'GET', body } = {}) {
  const indicator = document.querySelector('[data-testid="loading-indicator"]');
  pending++; if (indicator) indicator.hidden = false;
  try {
    let response;
    try { response = await fetch(`/api${path}`, { method, credentials: 'same-origin', headers: body === undefined ? {} : { 'Content-Type': 'application/json' }, ...(body === undefined ? {} : { body: JSON.stringify(body) }) }); }
    catch { throw new ApiError('Không kết nối được máy chủ. Kiểm tra server rồi thử lại.'); }
    let result;
    try { result = await response.json(); } catch { throw new ApiError('Máy chủ không trả về dữ liệu JSON. Vui lòng thử lại.', response.status); }
    if (!response.ok || !result.success) throw new ApiError(result.message, response.status, result.errors || {});
    return result;
  } finally { pending--; if (indicator) indicator.hidden = pending === 0; }
}
export function query(values) {
  return new URLSearchParams(Object.entries(values).filter(([, value]) => value !== '' && value !== undefined && value !== null)).toString();
}
