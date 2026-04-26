import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export function SignIn() {
    const [showPassword, setShowPassword] = useState(false);
    const [loginMethod, setLoginMethod] = useState('email'); // 'email' or 'phone'
    const [email, setEmail] = useState('');
    const [phone, setPhone] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const location = useLocation();
    const { signIn } = useAuth();

    const handleSubmit = async () => {
        setError('');
        if (loginMethod === 'email' && !email.trim()) {
            setError('Email is required');
            return;
        }
        if (loginMethod === 'phone' && !phone.trim()) {
            setError('Phone number is required');
            return;
        }
        if (!password.trim()) {
            setError('Password is required');
            return;
        }

        setIsLoading(true);

        try {
            const signedInUser = await signIn({
                email: loginMethod === 'email' ? email.trim() : undefined,
                phone: loginMethod === 'phone' ? phone.trim() : undefined,
                password,
            });

            const redirectPath = location.state?.from?.pathname || '/';
            navigate(redirectPath, { replace: true });
        } catch (err) {
            setError(err?.response?.data?.detail || err.message || 'Unable to sign in');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">

            {/* Login Card */}
            <div className="relative w-full max-w-md">
                <div className="bg-white rounded-3xl shadow-2xl overflow-hidden backdrop-blur-lg">
                    {/* Header */}
                    <div className="px-8 pt-8 pb-6 text-center">
                        <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl mb-4 shadow-lg">
                            <span className="text-4xl">🔐</span>
                        </div>
                        <h1 className="text-3xl font-bold text-gray-800 mb-2">Welcome Back</h1>
                        <p className="text-gray-500">Sign in to continue to your account</p>
                    </div>

                    {/* Form */}
                    <div className="px-8 pb-8 space-y-6">
                        {/* Login Method Toggle */}
                        <div className="flex bg-gray-100 rounded-xl p-1">
                            <button
                                type="button"
                                onClick={() => setLoginMethod('email')}
                                className={`cursor-pointer flex-1 py-2 px-4 rounded-lg font-medium text-sm transition duration-200 ${loginMethod === 'email'
                                        ? 'bg-white text-indigo-600 shadow-sm'
                                        : 'text-gray-600 hover:text-gray-800'
                                    }`}
                            >
                                📧 Email
                            </button>
                            <button
                                type="button"
                                onClick={() => setLoginMethod('phone')}
                                className={`cursor-pointer flex-1 py-2 px-4 rounded-lg font-medium text-sm transition duration-200 ${loginMethod === 'phone'
                                        ? 'bg-white text-indigo-600 shadow-sm'
                                        : 'text-gray-600 hover:text-gray-800'
                                    }`}
                            >
                                📱 Mobile
                            </button>
                        </div>

                        {error && (
                            <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                                {error}
                            </div>
                        )}

                        {/* Email Input */}
                        {loginMethod === 'email' && (
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-700">Email Address</label>
                                <div className="relative">
                                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                                        <span className="text-gray-400">📧</span>
                                    </div>
                                    <input
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition duration-200"
                                        placeholder="you@example.com"
                                    />
                                </div>
                            </div>
                        )}

                        {loginMethod === 'phone' && (
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-gray-700">Mobile Number</label>
                                <div className="relative">
                                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                                        <span className="text-gray-400">📱</span>
                                    </div>
                                    <input
                                        type="tel"
                                        value={phone}
                                        onChange={(e) => setPhone(e.target.value)}
                                        className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition duration-200"
                                        placeholder="+91 0123456789"
                                    />
                                </div>
                            </div>
                        )}

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-gray-700">Password</label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                                    <span className="text-gray-400">🔒</span>
                                </div>
                                <input
                                    type={showPassword ? 'text' : 'password'}
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full pl-12 pr-12 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition duration-200"
                                    placeholder="Enter your password"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-gray-600 transition"
                                >
                                    <span className="text-xl">{showPassword ? '🙈' : '👁️'}</span>
                                </button>
                            </div>
                        </div>

                        {/* Remember Me & Forgot Password */}
                        <div className="flex items-center justify-between text-sm">
                            <label className="flex items-center cursor-pointer">
                                <input type="checkbox" className="w-4 h-4 text-purple-600 border-gray-300 rounded-full" />
                                <span className="ml-2 text-gray-600">Remember me</span>
                            </label>
                            <button onClick={() => alert('Forgot password clicked')} className="cursor-pointer text-indigo-600 hover:text-indigo-700 font-medium transition">
                                Forgot password?
                            </button>
                        </div>

                        {/* Submit Button */}
                        <button
                            onClick={handleSubmit}
                            disabled={isLoading}
                            className="cursor-pointer w-full py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl hover:scale-105 transform transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                        >
                            {isLoading ? (
                                <span className="flex items-center justify-center">
                                    <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    Signing in...
                                </span>
                            ) : (
                                '✨ Sign In'
                            )}
                        </button>

                        {/* Divider */}
                        <div className="relative">
                            <div className="absolute inset-0 flex items-center">
                                <div className="w-full border-t border-gray-200"></div>
                            </div>
                            <div className="relative flex justify-center text-sm">
                                <span className="px-4 bg-white text-gray-500">Or continue with</span>
                            </div>
                        </div>

                        {/* Social Login Buttons */}
                        {/* <div className="grid grid-cols-2 gap-4">
                            <button
                                onClick={() => alert('Google login clicked')}
                                className="flex items-center justify-center py-3 px-4 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 hover:shadow-md transition duration-200"
                            >
                                <span className="text-2xl mr-2">G</span>
                                <span className="text-sm font-medium text-gray-700">Google</span>
                            </button>
                            <button
                                onClick={() => alert('Facebook login clicked')}
                                className="flex items-center justify-center py-3 px-4 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 hover:shadow-md transition duration-200"
                            >
                                <span className="text-2xl mr-2">f</span>
                                <span className="text-sm font-medium text-gray-700">Facebook</span>
                            </button>
                        </div> */}

                        {/* Sign Up Link */}
                        <p className="text-center text-sm text-gray-600 flex justify-center gap-3">
                            <span>Don't have an account ?</span>
                            <Link to={"/signUp"} className="cursor-pointer text-indigo-600 hover:text-indigo-700 font-semibold transition">
                                Sign up →
                            </Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}