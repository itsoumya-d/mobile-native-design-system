// Generated native motion contract.
import { AccessibilityInfo, Animated, Easing } from 'react-native';

export type MobileMotionVariant = 'rest' | 'pressed' | 'detail';
export const mobileMotion = {
  sharedTransitionId: 'native-status-card',
  totalDuration: 330,
  interruptionPolicy: 'retarget',
  restingState: 'rest' as MobileMotionVariant,
  gesture: { kind: 'tap', threshold: 0, cancel: 'return-to-rest' },
  reducedMotion: 'opacity',
  shouldReduceMotion: () => AccessibilityInfo.isReduceMotionEnabled(),
  animateOpacity: (value: Animated.Value, toValue: number) =>
    Animated.timing(value, {
      toValue,
      duration: 330,
      easing: Easing.out(Easing.cubic),
      useNativeDriver: true,
    }),
} as const;
