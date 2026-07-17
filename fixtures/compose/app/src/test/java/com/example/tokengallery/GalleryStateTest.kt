package com.example.tokengallery

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class GalleryStateTest {
    @Test
    fun `expanded width uses two content columns`() {
        assertEquals(2, GalleryLayout.columnsFor(widthDp = 840f, fontScale = 1f))
    }

    @Test
    fun `large text keeps gallery in one column`() {
        assertEquals(1, GalleryLayout.columnsFor(widthDp = 840f, fontScale = 1.6f))
    }

    @Test
    fun `retry action returns error state to populated`() {
        val error = GalleryState(content = ContentState.Error)
        assertEquals(ContentState.Populated, error.reduce(GalleryAction.Retry).content)
    }

    @Test
    fun `reduced motion removes decorative entrance`() {
        assertFalse(MotionPolicy(reduced = true).usesEntranceTranslation)
        assertTrue(MotionPolicy(reduced = false).usesEntranceTranslation)
    }
}
