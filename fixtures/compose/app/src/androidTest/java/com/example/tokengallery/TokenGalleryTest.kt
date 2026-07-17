package com.example.tokengallery

import androidx.compose.ui.test.assertHasClickAction
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithContentDescription
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class TokenGalleryTest {
    @get:Rule
    val composeRule = createComposeRule()

    @Test
    fun gallery_exposes_a_labeled_primary_action_and_navigation() {
        composeRule.setContent { TokenGalleryApp() }

        composeRule.onNodeWithText("Review plan").assertHasClickAction()
        composeRule.onNodeWithContentDescription("Open gallery navigation").assertIsDisplayed()
    }

    @Test
    fun retry_restores_the_populated_state() {
        composeRule.setContent { TokenGalleryApp(initialContent = ContentState.Error) }

        composeRule.onNodeWithText("Try again").performClick()
        composeRule.onNodeWithText("Build a buffer").assertIsDisplayed()
    }
}
