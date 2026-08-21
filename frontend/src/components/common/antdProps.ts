/**
 * Shared helpers for the hand-written antd wrapper components.
 *
 * The wrappers historically re-declared prop vocabularies antd never had
 * (most visibly `size: 'default'` vs antd's `'middle'`), producing dozens of
 * type errors and a few silent runtime no-ops. These utilities are the single
 * crossing point between the wrapper vocabulary and antd's.
 */
import type { SizeType } from 'antd/es/config-provider/SizeContext';

/** The size vocabulary the OpenLens wrappers expose. */
export type UiSize = 'small' | 'default' | 'large';

/** Map the wrapper vocabulary onto antd's ('default' -> 'middle'). */
export const toAntSize = (size?: UiSize): SizeType =>
  size === 'default' ? 'middle' : size;

/** Wrapper props = antd's props, minus what we re-declare, plus our own. */
export type WrapperProps<AntProps, Overrides = {}> =
  Omit<AntProps, keyof Overrides> & Overrides;
