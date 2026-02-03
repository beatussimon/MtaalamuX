import { View, Text, FlatList, StyleSheet, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { useConversations } from '../../src/hooks/useMessages';
import { Avatar } from '../../src/components/Avatar';
import { Loader, CardSkeleton } from '../../src/components/Loader';
import { formatRelativeTime } from '../../src/utils/helpers';
import { useAuthStore } from '../../src/store';

export default function MessagesScreen() {
  const router = useRouter();
  const { data: conversations, isLoading } = useConversations();
  const user = useAuthStore((state) => state.user);
  
  const getOtherParticipant = (participants: { id: number; username: string }[]) => {
    return participants.find((p) => p.id !== user?.id) || participants[0];
  };
  
  const renderConversation = ({ item }: { item: { id: number; participants: { id: number; username: string }[]; subject: string; last_message: { content: string; timestamp: string } | null; unread_count: number; consultation_status: { can_send_messages: boolean } } }) => {
    const other = getOtherParticipant(item.participants);
    const canMessage = item.consultation_status?.can_send_messages !== false;
    
    return (
      <TouchableOpacity className="flex-row items-center p-4 border-b border-secondary-100 bg-white" onPress={() => router.push({ pathname: '/messages/[id]', params: { id: item.id } })}>
        <Avatar source={null} name={other?.username || 'User'} size="md" />
        <View className="flex-1 ml-3">
          <View className="flex-row justify-between items-center">
            <Text className="font-semibold text-secondary-900">{other?.username || 'Unknown'}</Text>
            <Text className="text-xs text-secondary-400">{item.last_message ? formatRelativeTime(item.last_message.timestamp) : ''}</Text>
          </View>
          <Text className="text-sm text-secondary-600 mt-0.5" numberOfLines={1}>{item.subject}</Text>
          {!canMessage && <Text className="text-xs text-warning-500 mt-1">⚠️ Consultation ended</Text>}
        </View>
        {item.unread_count > 0 && <View className="bg-primary-600 rounded-full w-5 h-5 items-center justify-center ml-2"><Text className="text-white text-xs font-bold">{item.unread_count}</Text></View>}
      </TouchableOpacity>
    );
  };
  
  return (
    <View className="flex-1 bg-white">
      <View className="px-4 py-3 border-b border-secondary-100"><Text className="text-xl font-bold text-secondary-900">Messages</Text></View>
      <FlatList data={conversations} renderItem={renderConversation} keyExtractor={(item) => item.id.toString()} contentContainerStyle={styles.list}
        ListEmptyComponent={isLoading ? <View className="p-4 gap-3">{[1, 2, 3].map((i) => <CardSkeleton key={i} />)}</View> : (
          <View className="flex-1 items-center justify-center p-6">
            <Text className="text-5xl mb-4">💬</Text>
            <Text className="text-lg font-semibold text-secondary-900">No messages yet</Text>
            <Text className="text-secondary-500">Start a conversation with an expert</Text>
          </View>
        )} />
    </View>
  );
}

const styles = StyleSheet.create({ list: { flexGrow: 1 } });
