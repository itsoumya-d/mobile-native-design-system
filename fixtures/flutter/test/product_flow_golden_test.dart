import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:token_gallery/product_flow.dart';

void main() {
  testWidgets(
    'product sign-in keeps its compact visual contract',
    (tester) async {
      tester.view.physicalSize = const Size(390, 844);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);

      await tester.pumpWidget(const ProductFlowApp());
      await tester.pumpAndSettle();

      await expectLater(
        find.byType(ProductFlowApp),
        matchesGoldenFile('goldens/product-flow-sign-in.png'),
      );
    },
    tags: const <String>['golden'],
  );
}
