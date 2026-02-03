import '@testing-library/jest-native/extend-expect';
import { cleanup } from '@testing-library/react-native';

afterEach(() => cleanup());

jest.useFakeTimers();

const originalWarn = console.warn;
console.warn = (...args) => {
  if (typeof args[0] === 'string' && (args[0].includes('Animated') || args[0].includes('useNativeDriver'))) {
    return;
  }
  originalWarn.apply(console, args);
};
