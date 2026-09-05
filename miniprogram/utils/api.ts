import { request } from './request';
import { Card, EventItem, Space } from '../typings/index';

export function listSpaces(): Promise<Space[]> {
  return request<Space[]>({ url: '/api/spaces' });
}

export function getSpace(id: number): Promise<Space> {
  return request<Space>({ url: `/api/spaces/${id}` });
}

export function createSpace(name: string, type: string): Promise<Space> {
  return request<Space>({ url: '/api/spaces', method: 'POST', data: { name, type } });
}

export function listCards(spaceId: number): Promise<Card[]> {
  return request<Card[]>({ url: `/api/spaces/${spaceId}/cards` });
}

export function createCard(
  spaceId: number,
  data: { name: string; icon?: string; type: 'point' | 'duration' },
): Promise<Card> {
  return request<Card>({
    url: `/api/spaces/${spaceId}/cards`,
    method: 'POST',
    data,
  });
}

export function listEvents(spaceId: number, day?: string): Promise<EventItem[]> {
  const url = `/api/spaces/${spaceId}/events${day ? `?day=${day}` : ''}`;
  return request<EventItem[]>({ url });
}

export function createEvent(
  data: { space_id: number; card_id: number; end_at?: string | null },
): Promise<EventItem> {
  return request<EventItem>({ url: '/api/events', method: 'POST', data });
}

export function updateEvent(
  id: number,
  data: { end_at?: string | null },
): Promise<EventItem> {
  return request<EventItem>({ url: `/api/events/${id}`, method: 'PATCH', data });
}
