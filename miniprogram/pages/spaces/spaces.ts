import { createSpace, listSpaces } from '../../utils/api';
import { SPACE_TEMPLATES, Space } from '../../typings/index';

const app = getApp<{ globalData: { currentSpaceId: number } }>();

Page({
  data: {
    spaces: [] as Space[],
    templates: SPACE_TEMPLATES,
    showCreate: false,
    newName: '',
    selectedTemplate: 'custom',
    loading: false,
  },
  onShow() {
    this.fetchSpaces();
  },
  async fetchSpaces() {
    try {
      const spaces = await listSpaces();
      this.setData({ spaces });
    } catch (e) {
      wx.showToast({ title: (e as Error).message, icon: 'none' });
    }
  },
  onSelectSpace(e: WechatMiniprogram.TouchEvent) {
    const id = Number(e.currentTarget.dataset.id);
    app.globalData.currentSpaceId = id;
    wx.switchTab({ url: '/pages/timeline/timeline' });
  },
  onShowCreate() {
    this.setData({ showCreate: true, newName: '', selectedTemplate: 'custom' });
  },
  onCancelCreate() {
    this.setData({ showCreate: false });
  },
  onNameInput(e: WechatMiniprogram.Input) {
    this.setData({ newName: e.detail.value });
  },
  onSelectTemplate(e: WechatMiniprogram.TouchEvent) {
    this.setData({ selectedTemplate: String(e.currentTarget.dataset.key) });
  },
  async onCreate() {
    const name = this.data.newName.trim();
    if (!name) {
      wx.showToast({ title: '请输入空间名称', icon: 'none' });
      return;
    }
    this.setData({ loading: true });
    try {
      const space = await createSpace(name, this.data.selectedTemplate);
      app.globalData.currentSpaceId = space.id;
      this.setData({ showCreate: false, loading: false });
      wx.switchTab({ url: '/pages/timeline/timeline' });
    } catch (e) {
      this.setData({ loading: false });
      wx.showToast({ title: (e as Error).message, icon: 'none' });
    }
  },
});
