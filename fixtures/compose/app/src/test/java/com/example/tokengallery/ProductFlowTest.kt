package com.example.tokengallery

import org.junit.Assert.assertEquals
import org.junit.Test

class ProductFlowTest {
    @Test
    fun `retry restores the populated content state`() {
        val error = GalleryState(content = ContentState.Error)

        assertEquals(
            ContentState.Populated,
            error.reduce(GalleryAction.Retry).content,
        )
    }

    @Test
    fun `product routes cover authentication and the core flow`() {
        assertEquals(
            setOf(
                ProductRoute.SignIn,
                ProductRoute.Home,
                ProductRoute.Detail,
                ProductRoute.CheckIn,
                ProductRoute.Settings,
            ),
            ProductRoute.entries.toSet(),
        )
    }
}
