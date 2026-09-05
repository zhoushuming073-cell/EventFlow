export interface Space {
  id: number;
  name: string;
  type: string;
  owner_id: number;
  invite_code: string;
  created_at: string;
  role?: string;
  member_count?: number;
}

export interface Card {
  id: number;
  space_id: number;
  name: string;
  icon: string | null;
  type: 'point' | 'duration';
  sort_order: number;
  config: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface EventItem {
  id: number;
  space_id: number;
  card_id: number;
  user_id: number;
  start_at: string;
  end_at: string | null;
  data: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export const SPACE_TEMPLATES = [
  { key: 'baby', label: '宝宝', desc: '喝奶、睡觉、换尿布…' },
  { key: 'study', label: '学习', desc: '自习、上课、编程…' },
  { key: 'daily', label: '日常', desc: '通用日常记录' },
  { key: 'pet', label: '宠物', desc: '喂养、遛弯、健康…' },
  { key: 'custom', label: '自定义', desc: '空白空间，自己建卡片' },
];
