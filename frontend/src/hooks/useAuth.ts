import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { authApi, LoginRequest, RegisterRequest } from '@/api/auth';

export function useCurrentUser() {
  return useQuery({
    queryKey: ['currentUser'],
    queryFn: () => authApi.getCurrentUser(),
    retry: false,
  });
}

export function useLogin() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: LoginRequest) => authApi.login(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
    },
  });
}

export function useRegister() {
  return useMutation({
    mutationFn: (data: RegisterRequest) => authApi.register(data),
  });
}

export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: () => authApi.getUsers(),
  });
}
