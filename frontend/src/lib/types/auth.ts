export interface User {
  user_id: string
  email: string
  name: string
  role: string
}

export interface AuthState {
  isAuthenticated: boolean
  token: string | null
  user: User | null
  isLoading: boolean
  error: string | null
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface SignupCredentials {
  email: string
  password: string
  name: string
}

export interface AuthResponse {
  token: string
  user_id: string
  email: string
  name: string
  role: string
}
