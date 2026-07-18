import React from 'react';
import ReactTestRenderer, { act } from 'react-test-renderer';
import { ProductFlow } from '../src/ProductFlow';

describe('ProductFlow', () => {
  it('moves from authentication-shaped state to the product home', () => {
    let renderer: ReactTestRenderer.ReactTestRenderer;
    act(() => {
      renderer = ReactTestRenderer.create(<ProductFlow />);
    });

    const continueButton = renderer!.root.findByProps({
      accessibilityLabel: 'Continue securely',
    });
    act(() => continueButton.props.onPress());
    expect(JSON.stringify(renderer!.toJSON())).toContain('Available cash');
    act(() => renderer!.unmount());
  });

  it('keeps a semantic sign-in rendering snapshot', () => {
    let renderer: ReactTestRenderer.ReactTestRenderer;
    act(() => {
      renderer = ReactTestRenderer.create(<ProductFlow />);
    });

    expect(renderer!.toJSON()).toMatchSnapshot();
    act(() => renderer!.unmount());
  });
});
