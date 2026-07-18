// Generated native component contract.
import React from 'react';
import {
  ActivityIndicator,
  Pressable,
  StyleSheet,
  Text,
  View,
} from 'react-native';

export type NativeComponentState =
  | 'loading'
  | 'empty'
  | 'error'
  | 'populated';

export const nativeComponentContract = {
  subject: "calm financial wellbeing",
  userJob: "Understand one status and take the next safe action.",
  primaryActionLabel: "Try again",
} as const;

export function NativeStatusCard({
  title,
  state,
  onPrimaryAction,
}: {
  title: string;
  state: NativeComponentState;
  onPrimaryAction: () => void;
}): React.JSX.Element {
  const content =
    state === 'loading' ? (
      <ActivityIndicator accessibilityLabel="Loading" />
    ) : state === 'empty' ? (
      <Text>Nothing here yet</Text>
    ) : state === 'error' ? (
      <Text>Something went wrong</Text>
    ) : (
      <Text>{title}</Text>
    );
  return (
    <View
      accessible
      accessibilityLabel={`${title}, ${state}`}
      style={styles.card}
    >
      {content}
      <Pressable
        accessibilityRole="button"
        onPress={onPrimaryAction}
        style={styles.action}
      >
        <Text style={styles.actionLabel}>
          {nativeComponentContract.primaryActionLabel}
        </Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {borderRadius: 16, gap: 12, padding: 16},
  action: {
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 48,
    paddingHorizontal: 16,
  },
  actionLabel: {fontWeight: '600'},
});
