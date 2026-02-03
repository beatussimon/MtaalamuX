import { View, Text, ScrollView, StyleSheet, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { useAuthStore } from '../../src/store';
import { useTierInfo } from '../../src/hooks/useAuth';
import { Button } from '../../src/components/Button';
import { Loader } from '../../src/components/Loader';

export default function ConsultationsScreen() {
  const router = useRouter();
  const { data: tierInfo, isLoading } = useTierInfo();
  
  if (isLoading) return <Loader fullScreen text="Loading..." />;
  
  const canBook = tierInfo?.can_initiate_consultation === true;
  
  return (
    <ScrollView className="flex-1 bg-white">
      <View className="px-6 py-4 border-b border-secondary-100">
        <Text className="text-xl font-bold text-secondary-900">Consultations</Text>
        <Text className="text-secondary-500 mt-1">Book sessions with verified experts</Text>
      </View>
      
      <View className="px-6 py-4">
        {!canBook ? (
          <View className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-4">
            <Text className="text-2xl mb-2">🔒</Text>
            <Text className="font-semibold text-amber-800">Upgrade Required</Text>
            <Text className="text-sm text-amber-700 mt-1">You need Plus/Premium to book consultations.</Text>
            <Button title="Upgrade Now" className="mt-3" onPress={() => {}} />
          </View>
        ) : (
          <View className="bg-green-50 border border-green-200 rounded-xl p-4 mb-4">
            <Text className="text-2xl mb-2">✓</Text>
            <Text className="font-semibold text-green-800">Ready to book!</Text>
          </View>
        )}
        
        <Text className="text-lg font-bold text-secondary-900 mb-3">How it works</Text>
        <View className="gap-4">
          <View className="flex-row">
            <View className="w-8 h-8 bg-primary-100 rounded-full items-center justify-center"><Text className="text-primary-600 font-bold">1</Text></View>
            <View className="flex-1 ml-3"><Text className="font-medium text-secondary-900">Find an Expert</Text><Text className="text-sm text-secondary-500">Browse verified professionals</Text></View>
          </View>
          <View className="flex-row">
            <View className="w-8 h-8 bg-primary-100 rounded-full items-center justify-center"><Text className="text-primary-600 font-bold">2</Text></View>
            <View className="flex-1 ml-3"><Text className="font-medium text-secondary-900">Check Availability</Text><Text className="text-sm text-secondary-500">Select available time slots</Text></View>
          </View>
          <View className="flex-row">
            <View className="w-8 h-8 bg-primary-100 rounded-full items-center justify-center"><Text className="text-primary-600 font-bold">3</Text></View>
            <View className="flex-1 ml-3"><Text className="font-medium text-secondary-900">Book & Chat</Text><Text className="text-sm text-secondary-500">Message within consultation bounds</Text></View>
          </View>
        </View>
        
        <Button title="Find Experts" fullWidth className="mt-6" onPress={() => router.push('/(tabs)/discover')} disabled={!canBook} />
      </View>
    </ScrollView>
  );
}
