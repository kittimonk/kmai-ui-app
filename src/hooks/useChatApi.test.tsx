
import { describe, it, expect, vi } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useChatApi } from './useChatApi';

describe('useChatApi', () => {
  it('should initialize with default values', () => {
    const { result } = renderHook(() => useChatApi());
    
    expect(result.current.isLoading).toBe(false);
    expect(result.current.apiError).toBe(null);
  });

  it('should set loading state', () => {
    const { result } = renderHook(() => useChatApi());
    
    act(() => {
      result.current.setIsLoading(true);
    });
    
    expect(result.current.isLoading).toBe(true);
  });

  it('should set API error', () => {
    const { result } = renderHook(() => useChatApi());
    
    act(() => {
      result.current.setApiError('Test error');
    });
    
    expect(result.current.apiError).toBe('Test error');
  });
});
