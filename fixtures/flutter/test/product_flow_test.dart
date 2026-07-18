import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:token_gallery/product_flow.dart';

void main() {
  testWidgets('product flow signs in, opens detail, and saves a check-in', (
    tester,
  ) async {
    await tester.pumpWidget(const ProductFlowApp());

    await tester.tap(find.text('Continue securely'));
    await tester.pumpAndSettle();
    expect(find.text('Available cash'), findsOneWidget);

    await tester.tap(find.text('Emergency buffer'));
    await tester.pumpAndSettle();
    expect(find.text('Goal progress'), findsOneWidget);
  });

  testWidgets('check-in preserves the field and save navigation contract', (
    tester,
  ) async {
    await tester.pumpWidget(const ProductFlowApp());

    await tester.tap(find.text('Continue securely'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Check in'));
    await tester.pumpAndSettle();

    expect(find.text('What changed this week?'), findsOneWidget);
    await tester.enterText(find.byType(EditableText), 'Feeling prepared');
    await tester.tap(find.text('Save check-in'));
    await tester.pumpAndSettle();

    expect(find.text('Available cash'), findsOneWidget);
  });
}
