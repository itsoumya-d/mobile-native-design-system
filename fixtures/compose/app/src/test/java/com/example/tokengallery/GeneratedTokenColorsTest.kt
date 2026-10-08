package com.example.tokengallery

import androidx.compose.ui.graphics.toArgb
import mobile.tokens.MobileColorToken
import mobile.tokens.MobileTokens
import org.junit.Assert.assertEquals
import org.junit.Test

class GeneratedTokenColorsTest {
    @Test
    fun `generated white token decodes opaque ARGB`() {
        assertEquals(0xFFFFFFFF.toInt(), MobileTokens.color(MobileColorToken.primitivePaper).toArgb())
    }

    @Test
    fun `generated brand token preserves each color channel`() {
        assertEquals(0xFF09653A.toInt(), MobileTokens.color(MobileColorToken.actionPrimary).toArgb())
    }

    @Test
    fun `generated transparent token has zero alpha`() {
        assertEquals(0, MobileTokens.color(MobileColorToken.primitiveTransparent).toArgb())
    }
}
