import { BASE_URL, TOKEN_KEY, USER_ID_KEY } from './config';

export function getToken(): string {
  return wx.getStorageSync(TOKEN_KEY) || '';
}

export function setToken(token: string, userId: number): void {
  wx.setStorageSync(TOKEN_KEY, token);
  wx.setStorageSync(USER_ID_KEY, userId);
}

export function clearToken(): void {
  wx.removeStorageSync(TOKEN_KEY);
  wx.removeStorageSync(USER_ID_KEY);
}

export function getUserId(): number {
  return wx.getStorageSync(USER_ID_KEY) || 0;
}

/**
 * 自动登录：调用 wx.login 获取 code，换取后端 Token。
 * 返回 token；失败返回空字符串。
 */
export function login(): Promise<string> {
  return new Promise((resolve) => {
    wx.login({
      success: (res) => {
        if (!res.code) {
          resolve('');
          return;
        }
        wx.request({
          url: `${BASE_URL}/api/auth/wechat`,
          method: 'POST',
          data: { code: res.code },
          success: (resp) => {
            const body = resp.data as { token?: string; user_id?: number };
            if (body && body.token) {
              setToken(body.token, body.user_id || 0);
              resolve(body.token);
            } else {
              resolve('');
            }
          },
          fail: () => resolve(''),
        });
      },
      fail: () => resolve(''),
    });
  });
}
