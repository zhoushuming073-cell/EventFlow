import { createEvent, listCards, listEvents, updateEvent } from '../../utils/api';
import { Card, EventItem } from '../../typings/index';

const app = getApp<{ globalData: { currentSpaceId: number } }>();

function formatTime(iso: string): string {
  const d = new Date(iso);
  const hh = String(d.getHours()).padStart(2, '0');
  const mm = String(d.getMinutes()).padStart(2, '0');
  return `${hh}:${mm}`;
}

function todayStr(): string {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

interface DisplayEvent extends EventItem {
  cardName: string;
  cardIcon: string;
  startLabel: string;
  endLabel: string;
}

Page({
  data: {
    spaceId: 0,
    cards: [] as Card[],
    events: [] as DisplayEvent[],
    ongoing: null as DisplayEvent | null,
    loading: false,
  },
  onShow() {
    const spaceId = app.globalData.currentSpaceId;
    if (!spaceId) {
      wx.showToast({ title: '请先在「空间」页选择或创建空间', icon: 'none' });
      return;
    }
    this.setData({ spaceId });
    this.refresh();
  },
  async refresh() {
    const { spaceId } = this.data;
    if (!spaceId) return;
    this.setData({ loading: true });
    try {
      const [cards, events] = await Promise.all([
        listCards(spaceId),
        listEvents(spaceId, todayStr()),
      ]);
      const cardMap = new Map<number, Card>(cards.map((c) => [c.id, c]));
      const display: DisplayEvent[] = events.map((ev) => {
        const card = cardMap.get(ev.card_id);
        return {
          ...ev,
          cardName: card ? card.name : '未知',
          cardIcon: card ? card.icon || '📌' : '📌',
          startLabel: formatTime(ev.start_at),
          endLabel: ev.end_at ? formatTime(ev.end_at) : '进行中',
        };
      });
      const ongoing = display.find((ev) => ev.end_at === null) || null;
      this.setData({ cards, events: display, ongoing, loading: false });
    } catch (e) {
      this.setData({ loading: false });
      wx.showToast({ title: (e as Error).message, icon: 'none' });
    }
  },
  async onTapCard(e: WechatMiniprogram.TouchEvent) {
    const id = Number(e.currentTarget.dataset.id);
    const card = this.data.cards.find((c) => c.id === id);
    if (!card) return;

    if (card.type === 'point') {
      await this.recordPoint(card);
    } else {
      await this.startDuration(card);
    }
  },
  async recordPoint(card: Card) {
    try {
      await createEvent({ space_id: this.data.spaceId, card_id: card.id });
      wx.showToast({ title: `${card.name} 已记录`, icon: 'success' });
      this.refresh();
    } catch (e) {
      wx.showToast({ title: (e as Error).message, icon: 'none' });
    }
  },
  async startDuration(card: Card) {
    try {
      await createEvent({ space_id: this.data.spaceId, card_id: card.id });
      wx.showToast({ title: `${card.name} 开始`, icon: 'success' });
      this.refresh();
    } catch (e) {
      wx.showToast({ title: (e as Error).message, icon: 'none' });
    }
  },
  async onEndOngoing() {
    const { ongoing } = this.data;
    if (!ongoing) return;
    try {
      await updateEvent(ongoing.id, { end_at: null });
      wx.showToast({ title: `${ongoing.cardName} 已结束`, icon: 'success' });
      this.refresh();
    } catch (e) {
      wx.showToast({ title: (e as Error).message, icon: 'none' });
    }
  },
  onGoSpaces() {
    wx.switchTab({ url: '/pages/spaces/spaces' });
  },
});
