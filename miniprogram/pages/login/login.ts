import { login, getToken } from '../../utils/auth';

Page({
  data: {
    loading: false,
  },
  async onLogin() {
    this.setData({ loading: true });
    const token = await login();
    this.setData({ loading: false });
    if (token) {
      wx.switchTab({ url: '/pages/timeline/timeline' });
    } else {
      wx.showToast({ title: '登录失败，请重试', icon: 'none' });
    }
  },
  onLoad() {
    if (getToken()) {
      wx.switchTab({ url: '/pages/timeline/timeline' });
    }
  },
});
