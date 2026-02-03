import { View, ActivityIndicator, StyleSheet, Text } from 'react-native';
import { clsx } from 'clsx';

interface LoaderProps {
  size?: 'small' | 'large';
  color?: string;
  text?: string;
  fullScreen?: boolean;
}

export function Loader({ size = 'large', color = '#0ea5e9', text, fullScreen = false }: LoaderProps) {
  const content = (
    <View className="items-center justify-center p-4">
      <ActivityIndicator size={size} color={color} />
      {text && <Text className="text-secondary-500 mt-2 text-sm">{text}</Text>}
    </View>
  );
  
  if (fullScreen) {
    return <View className="flex-1 items-center justify-center bg-white">{content}</View>;
  }
  
  return content;
}

export function Skeleton({ className }: { className?: string }) {
  return <View className={clsx('bg-secondary-200 rounded animate-pulse', className)} />;
}

export function CardSkeleton() {
  return (
    <View className="bg-white rounded-xl p-4 shadow-sm border border-secondary-100">
      <View className="flex-row items-center mb-3">
        <Skeleton className="w-12 h-12 rounded-full" />
        <View className="ml-3 flex-1">
          <Skeleton className="h-4 w-32 mb-2" />
          <Skeleton className="h-3 w-24" />
        </View>
      </View>
      <Skeleton className="h-4 w-full mb-2" />
      <Skeleton className="h-4 w-3/4" />
    </View>
  );
}

export function MessageSkeleton() {
  return (
    <View className="flex-row items-end mb-4">
      <Skeleton className="w-8 h-8 rounded-full" />
      <View className="ml-2 flex-1">
        <View className="flex-row items-center mb-1">
          <Skeleton className="h-3 w-20" />
        </View>
        <Skeleton className="h-10 w-48 rounded-lg" />
      </View>
    </View>
  );
}
