import { TextInput, View, Text, StyleSheet } from 'react-native';
import { Controller, Control } from 'react-hook-form';
import { clsx } from 'clsx';

interface InputProps {
  name: string;
  control: Control<Record<string, unknown>>;
  label?: string;
  placeholder?: string;
  secureTextEntry?: boolean;
  keyboardType?: 'default' | 'email-address' | 'numeric' | 'phone-pad';
  autoCapitalize?: 'none' | 'sentences' | 'words' | 'characters';
  error?: string;
  multiline?: boolean;
  numberOfLines?: number;
  className?: string;
}

export function Input({
  name,
  control,
  label,
  placeholder,
  secureTextEntry = false,
  keyboardType = 'default',
  autoCapitalize = 'none',
  error,
  multiline = false,
  numberOfLines = 1,
  className,
}: InputProps) {
  return (
    <View className={clsx('mb-4', className)}>
      {label && (
        <Text className="text-secondary-700 font-medium mb-1 text-sm">
          {label}
        </Text>
      )}
      <Controller
        control={control}
        name={name}
        render={({ field: { onChange, onBlur, value } }) => (
          <TextInput
            value={value?.toString()}
            onChangeText={onChange}
            onBlur={onBlur}
            placeholder={placeholder}
            secureTextEntry={secureTextEntry}
            keyboardType={keyboardType}
            autoCapitalize={autoCapitalize}
            multiline={multiline}
            numberOfLines={multiline ? numberOfLines : undefined}
            placeholderTextColor="#94a3b8"
            className={clsx(
              'border rounded-lg px-4 py-3 bg-white',
              error ? 'border-red-500' : 'border-secondary-300',
              'text-secondary-900'
            )}
            style={styles.input}
          />
        )}
      />
      {error && (
        <Text className="text-red-500 text-xs mt-1">{error}</Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  input: {
    fontFamily: 'System',
    fontSize: 16,
    minHeight: 48,
  },
});
