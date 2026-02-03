import { useState } from 'react';
import { View, Text, KeyboardAvoidingView, Platform, ScrollView, StyleSheet } from 'react-native';
import { useRouter, Link } from 'expo-router';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useLogin } from '../../src/hooks/useAuth';
import { Button } from '../../src/components/Button';
import { Input } from '../../src/components/Input';
import { Loader } from '../../src/components/Loader';

const loginSchema = z.object({
  username: z.string().min(1, 'Username is required'),
  password: z.string().min(1, 'Password is required'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginScreen() {
  const router = useRouter();
  const { control, handleSubmit, formState: { errors } } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });
  const { mutate: login, isPending, isError, error } = useLogin();
  const [loading, setLoading] = useState(false);
  
  const onSubmit = async (data: LoginFormData) => {
    setLoading(true);
    try {
      await login(data);
      router.replace('/(tabs)/');
    } catch (err) {
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading || isPending) {
    return <Loader fullScreen text="Signing in..." />;
  }
  
  return (
    <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent} keyboardShouldPersistTaps="handled">
        <View className="flex-1 justify-center px-6 py-12">
          <View className="items-center mb-8">
            <Text className="text-4xl font-bold text-primary-600 mb-2">MtaalamuX</Text>
            <Text className="text-secondary-500">Connect with experts worldwide</Text>
          </View>
          
          <Text className="text-2xl font-bold text-secondary-900 mb-6">Welcome back</Text>
          
          {isError && (
            <View className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
              <Text className="text-red-600 text-sm">
                {(error as Error)?.message || 'Login failed. Please check your credentials.'}
              </Text>
            </View>
          )}
          
          <Input name="username" control={control} label="Username" placeholder="Enter your username" error={errors.username?.message} />
          <Input name="password" control={control} label="Password" placeholder="Enter your password" secureTextEntry error={errors.password?.message} />
          
          <Button title="Sign In" onPress={handleSubmit(onSubmit)} fullWidth className="mt-4" />
          
          <View className="flex-row justify-center mt-6">
            <Text className="text-secondary-500">Don't have an account? </Text>
            <Link href="/(auth)/register" asChild><Text className="text-primary-600 font-semibold">Sign Up</Text></Link>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#ffffff' },
  scrollContent: { flexGrow: 1 },
});
