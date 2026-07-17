import React from 'react';
import ReactTestRenderer, { act } from 'react-test-renderer';
import App, { layoutModeForWidth, motionSettingsFor } from '../App';

jest.mock('react-native-safe-area-context', () => {
  const ReactRuntime = require('react');
  const { View } = require('react-native');
  return {
    SafeAreaProvider: ({ children }: { children: React.ReactNode }) => children,
    SafeAreaView: ({ children }: { children: React.ReactNode }) =>
      ReactRuntime.createElement(View, null, children),
  };
});

describe('Token Gallery', () => {
  it('renders the financial wellbeing scale and component catalogue', () => {
    let renderer: ReactTestRenderer.ReactTestRenderer;
    act(() => {
      renderer = ReactTestRenderer.create(<App />);
    });

    const content = JSON.stringify(renderer!.toJSON());
    expect(content).toContain('Financial wellbeing');
    expect(content).toContain('Scale swatches');
    expect(content).toContain('Primary button');
    expect(content).toContain('Text field');
    expect(content).toContain('Cards');
    expect(content).toContain('List rows');
    expect(content).toContain('Loading');
    expect(content).toContain('Empty');
    expect(content).toContain('Error');
    expect(content).toContain('Navigation');
    expect(content).toContain('Accessibility stress');
    act(() => renderer!.unmount());
  });

  it('opens and dismisses the native modal from an accessible icon button', () => {
    let renderer: ReactTestRenderer.ReactTestRenderer;
    act(() => {
      renderer = ReactTestRenderer.create(<App />);
    });

    const open = renderer!.root.findByProps({
      accessibilityLabel: 'Open token details',
    });
    act(() => open.props.onPress());
    expect(JSON.stringify(renderer!.toJSON())).toContain('Token details');

    const dismiss = renderer!.root.findByProps({
      accessibilityLabel: 'Dismiss token details',
    });
    act(() => dismiss.props.onPress());
    expect(JSON.stringify(renderer!.toJSON())).not.toContain('Token details');
    act(() => renderer!.unmount());
  });

  it('selects explicit asynchronous states and preserves a retry action', () => {
    let renderer: ReactTestRenderer.ReactTestRenderer;
    act(() => {
      renderer = ReactTestRenderer.create(<App />);
    });

    const empty = renderer!.root.findByProps({
      accessibilityLabel: 'Show empty state',
    });
    act(() => empty.props.onPress());
    expect(JSON.stringify(renderer!.toJSON())).toContain('No planned payments');

    const error = renderer!.root.findByProps({
      accessibilityLabel: 'Show error state',
    });
    act(() => error.props.onPress());
    expect(JSON.stringify(renderer!.toJSON())).toContain('We could not refresh your plan');
    expect(
      renderer!.root.findByProps({ accessibilityLabel: 'Retry plan refresh' }),
    ).toBeTruthy();
    act(() => renderer!.unmount());
  });

  it('uses native compact, medium, and expanded layout modes and disables distance when requested', () => {
    expect(layoutModeForWidth(390)).toBe('compact');
    expect(layoutModeForWidth(720)).toBe('medium');
    expect(layoutModeForWidth(1024)).toBe('expanded');
    expect(motionSettingsFor(true)).toEqual({ duration: 0, distance: 0 });
  });
});
