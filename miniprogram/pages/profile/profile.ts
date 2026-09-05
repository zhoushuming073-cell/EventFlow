import { clearToken, getUserId } from '../../utils/auth';

Page({
  data: {
    userId: 0,
  },
  onShow() {
    this.setData({ userId: getUserId() });
  },
  onLogout() {
    wx.showModal({
      title: '退出登录',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          clearToken();
          wx.reLaunch({ url: '/pages/login/login' });
        }
      },
    });
  },
});
