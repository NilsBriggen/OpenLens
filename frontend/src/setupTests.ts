// Adds the jest-dom matchers (toBeInTheDocument, toHaveTextContent, ...) to
// Vitest's expect.
import '@testing-library/jest-dom/vitest';

// Node 26 ships an experimental global localStorage that is undefined without
// --localstorage-file, and it shadows jsdom's implementation. Install a real
// in-memory Storage so both `localStorage` and `window.localStorage` work.
class MemoryStorage implements Storage {
  private store = new Map<string, string>();
  get length() { return this.store.size; }
  clear() { this.store.clear(); }
  getItem(key: string) { return this.store.has(key) ? this.store.get(key)! : null; }
  key(index: number) { return [...this.store.keys()][index] ?? null; }
  removeItem(key: string) { this.store.delete(key); }
  setItem(key: string, value: string) { this.store.set(key, String(value)); }
}

const storage = new MemoryStorage();
Object.defineProperty(globalThis, 'localStorage', { value: storage, configurable: true });
if (typeof window !== 'undefined') {
  Object.defineProperty(window, 'localStorage', { value: storage, configurable: true });
}

// jsdom has no matchMedia; antd's responsive components require it.
if (typeof window !== 'undefined' && typeof window.matchMedia !== 'function') {
  Object.defineProperty(window, 'matchMedia', {
    configurable: true,
    value: (query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: () => {},
      removeListener: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
    }),
  });
}
