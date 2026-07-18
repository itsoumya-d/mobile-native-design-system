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
}
