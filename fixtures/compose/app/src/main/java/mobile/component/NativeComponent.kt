// Generated native component contract.
package mobile.component

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp

enum class NativeComponentState { Loading, Empty, Error, Populated }

object NativeComponentContract {
    const val subject: String = "calm financial wellbeing"
    const val userJob: String = "Understand one status and take the next safe action."
    const val primaryActionLabel: String = "Try again"
}

@Composable
fun NativeStatusCard(
    title: String,
    state: NativeComponentState,
    onPrimaryAction: () -> Unit,
    modifier: Modifier = Modifier,
) {
    Card(
        modifier = modifier.semantics {
            contentDescription = "$title, ${state.name}"
        },
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            when (state) {
                NativeComponentState.Loading -> CircularProgressIndicator()
                NativeComponentState.Empty -> Text("Nothing here yet")
                NativeComponentState.Error -> Text("Something went wrong")
                NativeComponentState.Populated -> Text(title)
            }
            Button(
                onClick = onPrimaryAction,
                modifier = Modifier.fillMaxWidth().heightIn(min = 48.dp),
            ) {
                Text(NativeComponentContract.primaryActionLabel)
            }
        }
    }
}
