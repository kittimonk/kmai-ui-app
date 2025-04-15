
import { describe, it, expect } from 'vitest';
import type { Message } from './chat';

describe('Message type', () => {
  it('should create a valid message object', () => {
    const message: Message = {
      id: '1',
      content: 'Hello world',
      sender: 'user',
      timestamp: new Date(),
    };

    expect(message).toHaveProperty('id');
    expect(message).toHaveProperty('content');
    expect(message).toHaveProperty('sender');
    expect(message).toHaveProperty('timestamp');
    expect(message.sender).toMatch(/^(user|bot)$/);
  });
});
