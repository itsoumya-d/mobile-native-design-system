import SwiftUI
import XCTest
@testable import TokenGallery

final class ProductFlowTests: XCTestCase {
    func testProductRouteContractCoversAuthenticationAndCoreFlow() {
        XCTAssertEqual(
            Set(ProductRoute.allCases),
            Set([.signIn, .home, .detail, .checkIn, .settings])
        )
    }

    @MainActor
    func testProductSignInProducesANativeSnapshot() throws {
        let renderer = ImageRenderer(
            content: SignInScreen(onContinue: {})
                .frame(width: 390, height: 844)
        )
        renderer.scale = 1

        let data = try XCTUnwrap(renderer.uiImage?.pngData())
        XCTAssertGreaterThan(data.count, 0)
    }
}
