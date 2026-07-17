import XCTest
@testable import TokenGallery

final class TokenContractTests: XCTestCase {
    func testCanonicalSpacingScaleIsComplete() {
        XCTAssertEqual(TokenCatalog.spacingScale, [0, 2, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64])
    }

    func testPlatformTouchTargetsMeetNativeMinimums() {
        XCTAssertGreaterThanOrEqual(TokenCatalog(profile: "ios").minimumTouchTarget, 44)
        XCTAssertGreaterThanOrEqual(TokenCatalog(profile: "android").minimumTouchTarget, 48)
    }

    func testReducedMotionRemovesDistanceAndDuration() {
        let reduced = TokenCatalog(profile: "reducedMotion")
        XCTAssertEqual(reduced.number("motion.distance.standard"), 0)
        XCTAssertEqual(reduced.durationMilliseconds("motion.duration.standard"), 0)
    }

    func testGalleryCoversEveryRequiredSurface() {
        XCTAssertEqual(
            Set(GallerySection.allCases),
            Set([.overview, .scales, .components, .states, .accessibility])
        )
    }
}
