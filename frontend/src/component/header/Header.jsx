import React from 'react'
import { Link } from "react-router-dom"
import { useAuth } from '../../context/AuthContext';

export function Header() {
    const { isAuthenticated, isAdmin, user, signOut } = useAuth();

    return (
        <nav className={`fixed w-full z-50 transition-all duration-300 bg-white shadow-lg
            }`}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 sm:py-4">
                <div className="flex justify-between items-center">
                    <Link to={"/"} className="flex items-center space-x-2 sm:space-x-3">
                        <div className="text-2xl sm:text-3xl lg:text-4xl">🤖</div>
                        <div>
                            <h1 className="text-lg sm:text-xl lg:text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                                AgenticAI Support
                            </h1>
                            <p className="text-[10px] sm:text-xs text-gray-500">Intelligent Customer Service</p>
                        </div>
                    </Link>
                    <div className="flex items-center space-x-2 sm:space-x-4 lg:space-x-6">
                        <div className="hidden md:flex space-x-4 lg:space-x-8 text-xs lg:text-sm font-medium">
                            <a href="#features" className="text-gray-700 hover:text-blue-600 transition">Features</a>
                            <a href="#industries" className="text-gray-700 hover:text-blue-600 transition">Industries</a>
                            <a href="#testimonials" className="text-gray-700 hover:text-blue-600 transition">Testimonials</a>
                            {isAdmin && (
                                <>
                                    <Link to={"/admin"} className="text-gray-700 hover:text-blue-600 transition">Admin</Link>
                                    <Link to={'/customers'} className="text-gray-700 hover:text-blue-600 transition">Customers</Link>
                                </>
                            )}
                        </div>
                        {isAuthenticated ? (
                            <>
                                <Link to={`/chat/${user?.customer_id}`} className="px-3 sm:px-4 lg:px-6 py-1.5 sm:py-2 text-xs sm:text-sm font-semibold text-gray-700 hover:text-blue-600 transition">
                                    Chat Now
                                </Link>
                                <div className="hidden sm:block text-xs text-gray-500">
                                    Signed in as <span className="font-semibold text-gray-700">{user?.name}</span>
                                </div>
                                <button onClick={signOut} className="px-3 sm:px-4 lg:px-6 py-1.5 sm:py-2 text-xs sm:text-sm font-semibold bg-slate-900 text-white rounded-full hover:shadow-lg transition transform hover:scale-105 cursor-pointer">
                                    Sign Out
                                </button>
                            </>
                        ) : (
                            <>
                                <Link to={"signIn"} className="px-3 sm:px-4 lg:px-6 py-1.5 sm:py-2 text-xs sm:text-sm font-semibold text-gray-700 hover:text-blue-600 transition">
                                    Sign In
                                </Link>
                                <Link to={"signUp"} className="px-3 sm:px-4 lg:px-6 py-1.5 sm:py-2 text-xs sm:text-sm font-semibold bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-full hover:shadow-lg transition transform hover:scale-105">
                                    Sign Up
                                </Link>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </nav>

    )
}

