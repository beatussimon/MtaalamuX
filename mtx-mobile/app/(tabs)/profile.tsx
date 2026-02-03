import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { useRouter } from 'expo-router';
import { useAuthStore } from '../../src/store';
import { useLogout, useTierInfo } from '../../src/hooks/useAuth';
import { Avatar } from '../../src/components/Avatar';
import { Button } from '../../src/components/Button';
import { Loader } from '../../src/components/Loader';

function MenuItem({ icon, label, onPress }: { icon: string; label: string; onPress: () => void }) {
  return (
    <TouchableOpacity className="flex-row items-center justify-between py-4 border-b border-secondary-100" onPress={onPress}>
      <View className="flex-row items-center">
        <Text className="text-xl mr-4">{icon}</Text>
        <Text className="text-secondary-900">{label}</Text>
      </View>
      <Text className="text-secondary-400">›</Text>
    </TouchableOpacity>
  );
}

export default function ProfileScreen() {
  const router = useRouter();
  const user = useAuthStore((state) => state.user);
  const profile = useAuthStore((state) => state.profile);
  const { data: tierInfo } = useTierInfo();
  const { mutate: logout, isPending } = useLogout();
  
  const handleLogout = async () => {
    await logout();
    router.replace('/(auth)/login');
  };
  
  if (!user) {
    return <Loader fullScreen text="Loading profile..." />;
  }
  
  return (
    <ScrollView className="flex-1 bg-white">
      <View className="bg-primary-600 px-6 pb-8 pt-12">
        <View className="items-center">
          <Avatar source={user.avatar ? { uri: user.avatar } : null} name={user.username} size="xl" showVerification verificationLevel={profile?.tier === 'premium' ? 'gold' : profile?.tier === 'plus' ? 'green' : null} />
          <Text className="text-white text-xl font-bold mt-3">{user.username}</Text>
          <Text className="text-primary-100">{user.email}</Text>
          {tierInfo && (
            <View className="bg-white/20 rounded-full px-4 py-1 mt-2">
              <Text className="text-white text-sm">{tierInfo.display_tier || profile?.display_tier}</Text>
            </View>
          )}
        </View>
      </View>
      
      <View className="px-6 -mt-4">
        <View className="bg-white rounded-xl shadow-sm p-4">
          <View className="flex-row justify-around">
            <View className="items-center">
              <Text className="text-xl font-bold text-secondary-900">✓</Text>
              <Text className="text-xs text-secondary-500">Premium</Text>
            </View>
            <View className="items-center">
              <Text className="text-xl font-bold text-secondary-900">{tierInfo?.can_initiate_consultation ? '✓' : '-'}</Text>
              <Text className="text-xs text-secondary-500">Consult</Text>
            </View>
            <View className="items-center">
              <Text className="text-xl font-bold text-secondary-900">{tierInfo?.can_post_content ? '✓' : '-'}</Text>
              <Text className="text-xs text-secondary-500">Publish</Text>
            </View>
          </View>
        </View>
      </View>
      
      <View className="px-6 py-4">
        <Text className="text-lg font-bold text-secondary-900 mb-2">Settings</Text>
        <View className="bg-white rounded-xl shadow-sm px-4">
          <MenuItem icon="✏️" label="Edit Profile" onPress={() => {}} />
          <MenuItem icon="🔔" label="Notifications" onPress={() => {}} />
          <MenuItem icon="🔒" label="Privacy" onPress={() => {}} />
          <MenuItem icon="🎨" label="Appearance" onPress={() => {}} />
          <MenuItem icon="❓" label="Help & Support" onPress={() => {}} />
          <MenuItem icon="ℹ️" label="About" onPress={() => {}} />
        </View>
      </View>
      
      <View className="px-6 py-4 pb-20">
        <Button title={isPending ? 'Signing out...' : 'Sign Out'} onPress={handleLogout} variant="danger" fullWidth />
      </View>
    </ScrollView>
  );
}
