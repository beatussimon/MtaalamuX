import { TouchableOpacity, Text, ActivityIndicator, StyleSheet, ViewStyle, TextStyle } from 'react-native';
import { clsx } from 'clsx';
import { ReactNode } from 'react';

interface ButtonProps {
  onPress: () => void;
  title?: string;
  children?: ReactNode;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
  className?: string;
}

const buttonStyles = {
  primary: 'bg-primary-600',
  secondary: 'bg-secondary-600',
  outline: 'border-2 border-primary-600 bg-transparent',
  ghost: 'bg-transparent',
  danger: 'bg-red-600',
};

const buttonTextStyles = {
  primary: 'text-white',
  secondary: 'text-white',
  outline: 'text-primary-600',
  ghost: 'text-primary-600',
  danger: 'text-white',
};

const sizeStyles = {
  sm: 'px-3 py-1.5',
  md: 'px-4 py-2',
  lg: 'px-6 py-3',
};

const textSizeStyles = {
  sm: 'text-sm',
  md: 'text-base',
  lg: 'text-lg',
};

export function Button({
  onPress,
  title,
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  fullWidth = false,
  className,
}: ButtonProps) {
  const isDisabled = disabled || loading;
  
  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={isDisabled}
      className={clsx(
        'rounded-lg items-center justify-center flex-row',
        buttonStyles[variant],
        sizeStyles[size],
        fullWidth && 'w-full',
        isDisabled && 'opacity-50',
        className
      )}
      style={styles.button}
      activeOpacity={0.7}
    >
      {loading && (
        <ActivityIndicator
          size="small"
          color={variant === 'outline' || variant === 'ghost' ? '#0ea5e9' : '#ffffff'}
          style={{ marginRight: 8 }}
        />
      )}
      {title && (
        <Text
          className={clsx('font-semibold', buttonTextStyles[variant], textSizeStyles[size])}
          style={styles.text}
        >
          {title}
        </Text>
      )}
      {children}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  button: {
    minWidth: 44,
    minHeight: 44,
  },
  text: {
    fontFamily: 'System',
  },
});
