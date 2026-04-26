import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { clearStoredAuth, getStoredAuth, setStoredAuth } from '../lib/authStorage';
import { getCurrentUser, loginUser, registerUser } from '../services/supportApi';

const AuthContext = createContext(null);
const ADMIN_EMAIL = 'mdnadimuddin62063@gmail.com';

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(null);
    const [isInitializing, setIsInitializing] = useState(true);

    useEffect(() => {
        const bootstrap = async () => {
            const stored = getStoredAuth();

            if (!stored?.token) {
                setIsInitializing(false);
                return;
            }

            setToken(stored.token);

            try {
                const currentUser = await getCurrentUser();
                setUser(currentUser);
                setStoredAuth({ token: stored.token, user: currentUser });
            } catch {
                clearStoredAuth();
                setToken(null);
                setUser(null);
            } finally {
                setIsInitializing(false);
            }
        };

        bootstrap();
    }, []);

    const persistAuth = (authResponse) => {
        const nextValue = {
            token: authResponse.access_token,
            user: authResponse.customer,
        };

        setToken(nextValue.token);
        setUser(nextValue.user);
        setStoredAuth(nextValue);
        return nextValue.user;
    };

    const signIn = async (credentials) => {
        const response = await loginUser(credentials);
        return persistAuth(response);
    };

    const signUp = async (payload) => {
        const response = await registerUser(payload);
        return persistAuth(response);
    };

    const signOut = () => {
        clearStoredAuth();
        setToken(null);
        setUser(null);
    };

    const value = useMemo(() => ({
        user,
        token,
        isInitializing,
        isAuthenticated: Boolean(token && user),
        isAdmin: Boolean(user?.email && user.email.toLowerCase() === ADMIN_EMAIL),
        signIn,
        signUp,
        signOut,
    }), [user, token, isInitializing]);

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}