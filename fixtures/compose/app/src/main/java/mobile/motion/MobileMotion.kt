// Generated native motion contract.
package mobile.motion

import androidx.compose.animation.core.tween
import androidx.compose.ui.MotionDurationScale
import kotlin.coroutines.coroutineContext

enum class MobileMotionVariant { REST, PRESSED, DETAIL }

object MobileMotion {
    const val sharedTransitionId: String = "native-status-card"
    const val totalDurationMillis: Int = 330
    const val interruptionPolicy: String = "retarget"
    val restingState = MobileMotionVariant.REST
    val opacity = tween<Float>(durationMillis = totalDurationMillis)

    suspend fun systemMotionEnabled(): Boolean =
        (coroutineContext[MotionDurationScale]?.scaleFactor ?: 1f) > 0f
}
