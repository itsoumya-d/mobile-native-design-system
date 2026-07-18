// Generated native motion contract.
import 'package:flutter/animation.dart';
import 'package:flutter/widgets.dart';

enum MobileMotionVariant { rest, pressed, detail }

class MobileMotion {
  const MobileMotion._();
  static const sharedTransitionId = 'native-status-card';
  static const totalDuration = Duration(milliseconds: 330);
  static const interruptionPolicy = 'retarget';
  static const restingState = MobileMotionVariant.rest;
  static const gestureKind = 'tap';
  static const gestureThreshold = 0;
  static const reducedMotionStrategy = 'opacity';

  static bool reduceMotion(BuildContext context) =>
      MediaQuery.disableAnimationsOf(context);

  static AnimationController controller(TickerProvider vsync) =>
      AnimationController(vsync: vsync, duration: totalDuration);

  static Animation<double> opacity(AnimationController controller) =>
      CurvedAnimation(parent: controller, curve: Curves.easeOutCubic);
}
