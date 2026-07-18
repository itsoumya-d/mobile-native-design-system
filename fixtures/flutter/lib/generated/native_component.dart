// Generated native component contract.
import 'package:flutter/material.dart';

enum NativeComponentState { loading, empty, error, populated }

class NativeStatusCard extends StatelessWidget {
  const NativeStatusCard({
    required this.title,
    required this.state,
    required this.onPrimaryAction,
    super.key,
  });

  static const subject = "calm financial wellbeing";
  static const userJob = "Understand one status and take the next safe action.";
  static const primaryActionLabel = "Try again";

  final String title;
  final NativeComponentState state;
  final VoidCallback onPrimaryAction;

  @override
  Widget build(BuildContext context) {
    final body = switch (state) {
      NativeComponentState.loading => const CircularProgressIndicator(),
      NativeComponentState.empty => const Text('Nothing here yet'),
      NativeComponentState.error => const Text('Something went wrong'),
      NativeComponentState.populated => Text(title),
    };
    return Semantics(
      container: true,
      label: '$title, ${state.name}',
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              body,
              const SizedBox(height: 12),
              FilledButton(
                onPressed: onPrimaryAction,
                child: const Text(primaryActionLabel),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
