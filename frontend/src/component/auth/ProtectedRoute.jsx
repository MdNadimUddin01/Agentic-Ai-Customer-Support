import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export function ProtectedRoute({ children, requireAdmin = false }) {
    const location = useLocation();
    const { isAuthenticated, isInitializing, isAdmin } = useAuth();

    if (isInitializing) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-slate-50 text-slate-600">
                Checking your session...
            </div>
        );
    }

    if (!isAuthenticated) {
        return <Navigate to="/signIn" replace state={{ from: location }} />;
    }

    if (requireAdmin && !isAdmin) {
        return <Navigate to="/" replace />;
    }

    return children;
}