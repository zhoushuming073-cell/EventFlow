import { BASE_URL } from './config';
import { clearToken, getToken, login } from './auth';

interface RequestOptions {
  url: string;
  method?: 'GET' | 'POST' | 'PATCH' | 'DELETE';
  data?: Record<string, unknown>;
}

interface RequestResult<T> {
  statusCode: number;
  data: T;
}

/**
 * 统一请求封装：
 * - 自动附加 Bearer Token
 * - 遇到 401 时清理 Token 并自动重新登录重试一次
 */
export function request<T = unknown>(options: RequestOptions): Promise<T> {
  return doRequest<T>(options).then((res) => res.data);
}

function doRequest<T = unknown>(
  options: RequestOptions,
  isRetry = false,
): Promise<RequestResult<T>> {
  return new Promise((resolve, reject) => {
    const header: Record<string, string> = {
      'content-type': 'application/json',
    };
    const token = getToken();
    if (token) {
      header.Authorization = `Bearer ${token}`;
    }

    wx.request({
      url: `${BASE_URL}${options.url}`,
      // 微信类型定义未收录 PATCH，运行时支持，这里显式断言
      method: (options.method || 'GET') as WechatMiniprogram.RequestOption['method'],
      data: options.data,
      header,
      success: (resp) => {
        const statusCode = resp.statusCode;

        // 401：清理 Token 并尝试重新登录后重试一次
        if (statusCode === 401 && !isRetry) {
          clearToken();
          login().then((newToken) => {
            if (!newToken) {
              reject(new Error('重新登录失败'));
              return;
            }
            doRequest<T>(options, true).then(resolve).catch(reject);
          });
          return;
        }

        if (statusCode >= 200 && statusCode < 300) {
          resolve({ statusCode, data: resp.data as T });
        } else {
          const detail =
            (resp.data as { detail?: string } | undefined)?.detail ||
            `请求失败(${statusCode})`;
          reject(new Error(detail));
        }
      },
      fail: (err) => reject(new Error(err.errMsg || '网络错误')),
    });
  });
}
