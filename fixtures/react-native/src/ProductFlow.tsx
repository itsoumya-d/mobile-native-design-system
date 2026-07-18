import React, { useEffect, useMemo, useState } from 'react';
import {
  AccessibilityInfo,
  ActivityIndicator,
  I18nManager,
  Modal,
  Pressable,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  TextInput,
  useWindowDimensions,
  View,
} from 'react-native';

export type ProductRoute =
  | 'sign-in'
  | 'home'
  | 'detail'
  | 'check-in'
  | 'settings';
type LoadState = 'loading' | 'empty' | 'error' | 'populated';
type Navigation = { navigate: (route: ProductRoute) => void; back: () => void };

export const PRODUCT_ROUTES = [
  { name: 'sign-in', component: SignInScreen },
  { name: 'home', component: HomeScreen },
  { name: 'detail', component: DetailScreen },
  { name: 'check-in', component: CheckInFormScreen },
  { name: 'settings', component: SettingsScreen },
] as const;

const repository = {
  async save(note: string) {
    return note.trim();
  },
};

function ProductButton({
  label,
  onPress,
}: {
  label: string;
  onPress: () => void;
}) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={label}
      onPress={onPress}
      style={({ pressed }) => [styles.button, { opacity: pressed ? 0.86 : 1 }]}
    >
      <Text style={styles.buttonLabel}>{label}</Text>
    </Pressable>
  );
}

export function SignInScreen({ navigation }: { navigation: Navigation }) {
  return (
    <View style={styles.centered}>
      <Text accessibilityRole="header" style={styles.title}>
        Your next money decision, made calmer.
      </Text>
      <ProductButton
        label="Continue securely"
        onPress={() => navigation.navigate('home')}
      />
    </View>
  );
}

export function HomeScreen({ navigation }: { navigation: Navigation }) {
  const [state, setState] = useState<LoadState>('populated');
  const [sheetVisible, setSheetVisible] = useState(false);
  const { width, fontScale } = useWindowDimensions();
  const contentWidth = width >= 720 && fontScale < 1.4 ? 680 : width;
  const adaptiveContentStyle = useMemo(
    () =>
      StyleSheet.create({
        content: { maxWidth: contentWidth, alignSelf: 'center' },
      }).content,
    [contentWidth],
  );

  return (
    <View style={styles.screen}>
      <View style={styles.navigation}>
        <Text accessibilityRole="header" style={styles.heading}>
          Today
        </Text>
        <Pressable
          accessibilityRole="button"
          accessibilityLabel="Open settings"
          onPress={() => navigation.navigate('settings')}
          style={styles.iconButton}
        >
          <Text>⚙</Text>
        </Pressable>
      </View>
      <ScrollView
        contentContainerStyle={[styles.content, adaptiveContentStyle]}
      >
        <Text style={styles.label}>Available cash</Text>
        <Text style={styles.balance}>₹ 12,480</Text>
        {state === 'loading' ? (
          <View accessibilityLiveRegion="polite" style={styles.message}>
            <ActivityIndicator />
            <Text>Loading plans</Text>
          </View>
        ) : state === 'empty' ? (
          <View style={styles.message}>
            <Text style={styles.heading}>No plans yet</Text>
            <Text>Create a small check-in when you are ready.</Text>
          </View>
        ) : state === 'error' ? (
          <View style={styles.message}>
            <Text style={styles.heading}>Plans unavailable</Text>
            <Text>Your existing data is safe.</Text>
            <ProductButton
              label="Try again"
              onPress={() => setState('populated')}
            />
          </View>
        ) : (
          <>
            <Pressable
              accessibilityRole="button"
              accessibilityLabel="Open emergency buffer"
              onPress={() => navigation.navigate('detail')}
              style={styles.card}
            >
              <Text style={styles.heading}>Emergency buffer</Text>
              <Text>Two weeks of essential spending</Text>
            </Pressable>
            <Pressable
              accessibilityRole="button"
              accessibilityLabel="Review subscriptions"
              onPress={() => setSheetVisible(true)}
              style={styles.row}
            >
              <Text>Review subscriptions</Text>
              <Text>3 changes to consider</Text>
            </Pressable>
          </>
        )}
        <View style={styles.actions}>
          <ProductButton
            label="Check in"
            onPress={() => navigation.navigate('check-in')}
          />
          <ProductButton label="Show error" onPress={() => setState('error')} />
        </View>
      </ScrollView>
      <Modal
        visible={sheetVisible}
        transparent
        animationType="fade"
        onRequestClose={() => setSheetVisible(false)}
      >
        <View style={styles.scrim}>
          <View accessibilityViewIsModal style={styles.sheet}>
            <Text accessibilityRole="header" style={styles.heading}>
              Recommendation filters
            </Text>
            <Text>Choose which recommendations to review.</Text>
            <ProductButton
              label="Close filters"
              onPress={() => setSheetVisible(false)}
            />
          </View>
        </View>
      </Modal>
    </View>
  );
}

export function DetailScreen({ navigation }: { navigation: Navigation }) {
  return (
    <View style={styles.content}>
      <Text accessibilityRole="header" style={styles.title}>
        Emergency buffer
      </Text>
      <Text style={styles.heading}>Goal progress</Text>
      <Text>64% of the way to two weeks of essential spending.</Text>
      <ProductButton label="Back to today" onPress={navigation.back} />
    </View>
  );
}

export function CheckInFormScreen({ navigation }: { navigation: Navigation }) {
  const [note, setNote] = useState('');
  const [saving, setSaving] = useState(false);
  const submit = async () => {
    setSaving(true);
    await repository.save(note);
    navigation.navigate('home');
  };
  return (
    <View style={styles.content}>
      <Text accessibilityRole="header" style={styles.title}>
        Weekly check-in
      </Text>
      <TextInput
        accessibilityLabel="What changed this week?"
        multiline
        value={note}
        onChangeText={setNote}
        style={styles.field}
      />
      <ProductButton
        label={saving ? 'Saving' : 'Save check-in'}
        onPress={submit}
      />
    </View>
  );
}

export function SettingsScreen({ navigation }: { navigation: Navigation }) {
  const [reminders, setReminders] = useState(true);
  return (
    <View style={styles.content}>
      <Text accessibilityRole="header" style={styles.title}>
        Settings
      </Text>
      <View style={styles.row}>
        <View>
          <Text style={styles.heading}>Weekly reminders</Text>
          <Text>Friday at 9:00</Text>
        </View>
        <Switch
          accessibilityLabel="Weekly reminders"
          value={reminders}
          onValueChange={setReminders}
        />
      </View>
      <Text>
        {I18nManager.isRTL ? 'العربية' : 'English and Arabic fixture'}
      </Text>
      <ProductButton label="Done" onPress={navigation.back} />
    </View>
  );
}

export function ProductFlow() {
  const [route, setRoute] = useState<ProductRoute>('sign-in');
  const [_history, setHistory] = useState<ProductRoute[]>([]);
  const [reduceMotion, setReduceMotion] = useState(false);

  useEffect(() => {
    AccessibilityInfo.isReduceMotionEnabled().then(setReduceMotion);
  }, []);

  const navigation = useMemo<Navigation>(
    () => ({
      navigate: next => {
        setHistory(current => [...current, route]);
        setRoute(next);
      },
      back: () => {
        setHistory(current => {
          const next = [...current];
          setRoute(next.pop() ?? 'home');
          return next;
        });
      },
    }),
    [route],
  );

  const Screen = PRODUCT_ROUTES.find(item => item.name === route)!.component;
  return (
    <View
      accessibilityLabel="Financial wellbeing product flow"
      style={[
        styles.root,
        reduceMotion ? styles.motionReduced : styles.motionEnabled,
      ]}
    >
      <Screen navigation={navigation} />
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: '#F4F7F5' },
  motionReduced: { opacity: 1 },
  motionEnabled: { opacity: 0.999 },
  screen: { flex: 1 },
  centered: {
    flex: 1,
    justifyContent: 'center',
    padding: 24,
    gap: 24,
    maxWidth: 520,
    alignSelf: 'center',
  },
  navigation: {
    minHeight: 64,
    paddingHorizontal: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  content: { width: '100%', padding: 24, gap: 16 },
  title: { fontSize: 30, lineHeight: 38, fontWeight: '800' },
  heading: { fontSize: 18, lineHeight: 25, fontWeight: '700' },
  label: { fontSize: 15, lineHeight: 21 },
  balance: { fontSize: 36, lineHeight: 44, fontWeight: '800' },
  button: {
    minHeight: 48,
    borderRadius: 14,
    paddingHorizontal: 20,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#16623B',
  },
  buttonLabel: { color: '#FFFFFF', fontWeight: '700' },
  iconButton: {
    width: 48,
    minHeight: 48,
    alignItems: 'center',
    justifyContent: 'center',
  },
  card: {
    minHeight: 88,
    borderRadius: 20,
    padding: 18,
    gap: 4,
    backgroundColor: '#FFFFFF',
  },
  row: {
    minHeight: 56,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 12,
  },
  message: {
    minHeight: 180,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 12,
  },
  actions: { gap: 12, marginTop: 24 },
  field: {
    minHeight: 112,
    borderWidth: 1,
    borderColor: '#65736B',
    borderRadius: 14,
    padding: 14,
    textAlignVertical: 'top',
  },
  scrim: { flex: 1, justifyContent: 'flex-end', backgroundColor: '#00000066' },
  sheet: {
    borderTopLeftRadius: 28,
    borderTopRightRadius: 28,
    backgroundColor: '#FFFFFF',
    padding: 24,
    gap: 16,
  },
});
