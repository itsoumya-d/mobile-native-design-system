import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:token_gallery/main.dart';

void main() {
  test('expanded layout uses two gallery columns unless text is large', () {
    expect(GalleryLayout.columnsFor(width: 900, textScale: 1), 2);
    expect(GalleryLayout.columnsFor(width: 900, textScale: 1.6), 1);
  });

  test('reduced motion disables decorative translation', () {
    expect(MotionPolicy(reduced: true).entranceOffset, Offset.zero);
    expect(MotionPolicy(reduced: false).entranceOffset, const Offset(0, 16));
  });

  testWidgets(
    'gallery exposes labeled controls and required component surfaces',
    (tester) async {
      await tester.pumpWidget(const TokenGalleryApp());

      expect(find.text('Financial wellbeing'), findsOneWidget);
      expect(find.text('Buttons'), findsOneWidget);
      expect(find.bySemanticsLabel('Open gallery navigation'), findsOneWidget);
      expect(find.bySemanticsLabel('Open token details'), findsOneWidget);
      expect(find.byType(TextField), findsOneWidget);
      expect(find.text('Review plan'), findsOneWidget);

      await tester.ensureVisible(find.text('Review plan'));
      await tester.tap(find.text('Review plan'));
      await tester.pump();
      expect(find.text('Plan review'), findsOneWidget);
    },
  );

  testWidgets(
    'RTL, largest text, tablet width, and reduced motion stay usable',
    (tester) async {
      tester.view.physicalSize = const Size(1400, 900);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);

      await tester.pumpWidget(
        const MaterialApp(
          home: MediaQuery(
            data: MediaQueryData(textScaler: TextScaler.linear(1.6)),
            child: Directionality(
              textDirection: TextDirection.rtl,
              child: TokenGalleryApp(reducedMotion: true),
            ),
          ),
        ),
      );

      expect(find.text('Financial wellbeing'), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets('interactive controls meet Flutter accessibility guidelines', (
    tester,
  ) async {
    await tester.pumpWidget(const TokenGalleryApp());

    expect(tester, meetsGuideline(androidTapTargetGuideline));
    expect(tester, meetsGuideline(labeledTapTargetGuideline));
  });

  testWidgets('retry restores the error sample', (tester) async {
    await tester.pumpWidget(const TokenGalleryApp());

    await tester.ensureVisible(find.text('Try again'));
    await tester.tap(find.text('Try again'));
    await tester.pump();

    expect(find.text('Restored'), findsOneWidget);
  });
}
