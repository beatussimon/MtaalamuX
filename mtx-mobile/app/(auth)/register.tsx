import { useState } from 'react';
import { View, Text, KeyboardAvoidingView, Platform, ScrollView, StyleSheet } from 'react-native';
import { useRouter, Link } from 'expo-router';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useRegister } from '../../src/hooks/useAuth';
import { Button } from '../../src/components/Button';
import { Input } from '../../src/components/Input';
import { Loader } from '../../src/components/Loader';

const registerSchema = z.object({
  username: z.string().min(3, 'Username must be at least 3 characters'),
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  password2: z.string(),
  first_name: z.string().optional(),
  last_name: z.string().optional(),
}).refine((data) => data.password === data.password2, {
  message: "Passwords don't match",
  path: ['password2'],
});

type RegisterFormData = z.infer<typeof registerSchema>;

export default function RegisterScreen() {
  const router = useRouter();
  const { control, handleSubmit, formState: { errors } } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });
  const { mutate: registerUser, isPending, isError, error } = useRegister();
  const [loading, setLoading] = useState(false);
  
  const onSubmit = async (data: RegisterFormData) => {
    setLoading(true);
    try {
      await registerUser(data);
      router.replace('/(tabs)/');
    } catch (err) {
      console.error('Registration error:', err);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading || isPending) {
    return <Loader fullScreen text="Creating account..." />;
  }
  
  return (
    <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent} keyboardShouldPersistTaps="handled">
        <View className="flex-1 justify-center px-6 py-12">
          <View className="items-center mb-8">
            <Text className="text-4xl font-bold text-primary-600 mb-2">MtaalamuX</Text>
            <Text className="text-secondary-500">Create your account</Text>
          </View>
          <Text className="text-2xl font-bold text-secondary-900 mb-6">Sign Up</Text>
          
          {isError && (
            <View className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
              <Text className="text-red-600 text-sm">{(error as Error)?.message || 'Registration failed'}</Text>
            </View>
          )}
          
          <View className="flex-row">
            <View className="flex-1 mr-2">
              <Input name="first_name" control={control} label="First Name" placeholder="Optional" autoCapitalize="words" />
            </View>
            <View className="flex-1 ml-2">
              <Input name="last_name" control={control} label="Last Name" placeholder="Optional" autoCapitalize="words" />
            </View>
          </View>
          
          <Input name="username" control={control} label="Username" placeholder="Choose a username" error={errors.username?.message} />
          <Input name="email" control={control} label="Email" placeholder="Enter your email" keyboardType="email-address" error={errors.email?.message} />
          <Input name="password" control={control} label="Password" placeholder="Create a password" secureTextEntry error={errors.password?.message} />
          <Input name="password2" control={control} label="Confirm Password" placeholder="Confirm your password" secureTextEntry error={errors.password2?.message} />
          
          <Button title="Create Account" onPress={handleSubmit(onSubmit)} fullWidth className="mt-4" />
          
          <View className="flex-row justify-center mt-6">
            <Text className="text-secondary-500">Already have an account? </Text>
            <Link href="/(auth)/login" asChild><Text className="text-primary-600 font-semibold">Sign In</Text></Link>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({ container: { flex: 1, backgroundColor: '#ffffff' }, scrollContent: { flexGrow: 1 } });
