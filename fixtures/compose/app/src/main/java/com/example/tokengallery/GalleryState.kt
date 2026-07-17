package com.example.tokengallery

enum class ContentState { Populated, Loading, Empty, Error }

enum class GalleryAction { Retry }

data class GalleryState(
    val content: ContentState = ContentState.Populated,
    val sheetVisible: Boolean = false,
    val dialogVisible: Boolean = false,
    val reducedMotion: Boolean = false,
    val highContrast: Boolean = false,
) {
    fun reduce(action: GalleryAction): GalleryState = when (action) {
        GalleryAction.Retry -> copy(content = ContentState.Populated)
    }
}

data class MotionPolicy(val reduced: Boolean) {
    val usesEntranceTranslation: Boolean = !reduced
    val durationMillis: Int = if (reduced) 0 else 240
}

object GalleryLayout {
    fun columnsFor(widthDp: Float, fontScale: Float): Int =
        if (widthDp >= 840f && fontScale < 1.4f) 2 else 1
}
