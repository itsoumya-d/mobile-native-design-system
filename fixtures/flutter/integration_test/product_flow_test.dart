import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:token_gallery/product_flow.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('native product flow preserves navigation and form behavior', (
    tester,
  ) async {
    await tester.pumpWidget(const ProductFlowApp());

    await tester.tap(find.text('Continue securely'));
    await tester.pumpAndSettle();
    expect(find.text('Available cash'), findsOneWidget);

    await tester.tap(find.text('Check in'));
    await tester.pumpAndSettle();
    expect(find.text('How are you feeling?'), findsOneWidget);

    await tester.enterText(find.byType(EditableText), 'Feeling prepared');
    await tester.tap(find.text('Save check-in'));
    await tester.pumpAndSettle();
    expect(find.text('Available cash'), findsOneWidget);
  });
}
