import { getToken, login } from './utils/auth';

App({
  globalData: {
    currentSpaceId: 0,
  },
  onLaunch() {
    // 已有 Token 则跳过；否则自动登录
    if (!getToken()) {
      login();
    }
  },
});
