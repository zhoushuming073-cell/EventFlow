import { createCard, listCards } from '../../utils/api';
import { Card } from '../../typings/index';

const app = getApp<{ globalData: { currentSpaceId: number } }>();

Page({
  data: {
    spaceId: 0,
    cards: [] as Card[],
    showCreate: false,
    newName: '',
    newIcon: '',
    newType: 'point',
    loading: false,
  },
  onShow() {
    const spaceId = app.globalData.currentSpaceId;
    if (!spaceId) {
      wx.showToast({ title: '请先选择空间', icon: 'none' });
      return;
    }
    this.setData({ spaceId });
    this.fetchCards();
  },
  async fetchCards() {
    try {
      const cards = await listCards(this.data.spaceId);
      this.setData({ cards });
    } catch (e) {
      wx.showToast({ title: (e as Error).message, icon: 'none' });
    }
  },
  onShowCreate() {
    this.setData({ showCreate: true, newName: '', newIcon: '', newType: 'point' });
  },
  onCancelCreate() {
    this.setData({ showCreate: false });
  },
  onNameInput(e: WechatMiniprogram.Input) {
    this.setData({ newName: e.detail.value });
  },
  onIconInput(e: WechatMiniprogram.Input) {
    this.setData({ newIcon: e.detail.value });
  },
  onSelectType(e: WechatMiniprogram.TouchEvent) {
    this.setData({ newType: String(e.currentTarget.dataset.type) });
  },
  async onCreate() {
    const name = this.data.newName.trim();
    if (!name) {
      wx.showToast({ title: '请输入卡片名称', icon: 'none' });
      return;
    }
    this.setData({ loading: true });
    try {
      await createCard(this.data.spaceId, {
        name,
        icon: this.data.newIcon || undefined,
        type: this.data.newType as 'point' | 'duration',
      });
      this.setData({ showCreate: false, loading: false });
      this.fetchCards();
    } catch (e) {
      this.setData({ loading: false });
      wx.showToast({ title: (e as Error).message, icon: 'none' });
    }
  },
});
