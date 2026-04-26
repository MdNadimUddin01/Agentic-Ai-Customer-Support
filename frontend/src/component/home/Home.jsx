import React, { useEffect, useState } from 'react';
import {Link} from "react-router-dom"
import { useAuth } from '../../context/AuthContext';
export function Home() {
    const [activeFeature, setActiveFeature] = useState(0);
    const [isScrolled, setIsScrolled] = useState(false);
    const { isAuthenticated, user } = useAuth();

    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 20);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const features = [
        {
            title: "Intelligent Order Management",
            description: "Verify missing packages, track shipments in real-time, and initiate replacements automatically through courier API integrations. Our AI understands complex delivery scenarios and provides instant resolutions.",
            icon: "📦",
            gradient: "from-blue-500 to-cyan-500",
            color: "bg-gradient-to-br from-blue-500 to-cyan-500"
        },
        {
            title: "Smart Payment Recovery",
            description: "Autonomously recover failed payments and adapt communication strategies based on customer payment history. Increase revenue while maintaining customer satisfaction.",
            icon: "💳",
            gradient: "from-purple-500 to-pink-500",
            color: "bg-gradient-to-br from-purple-500 to-pink-500"
        },
        {
            title: "Technical Troubleshooting",
            description: "Diagnose network issues, reset connections remotely, and schedule technician visits automatically. Resolve 90% of technical issues without human intervention.",
            icon: "🔧",
            gradient: "from-orange-500 to-red-500",
            color: "bg-gradient-to-br from-orange-500 to-red-500"

        },
        {
            title: "Multi-Channel Excellence",
            description: "Seamless customer interactions via WhatsApp, web interface, and native platform integration. Meet your customers where they are, anytime, anywhere.",
            icon: "💬",
            gradient: "from-green-500 to-teal-500",
            color: "bg-gradient-to-br from-blue-500 to-cyan-500"
        },
        {
            title: "Context-Aware Intelligence",
            description: "Leverages MongoDB vector database for semantic search, understanding customer intent beyond keywords. Retrieves relevant information from past interactions instantly.",
            icon: "🧠",
            gradient: "from-indigo-500 to-purple-500",
            color: "bg-gradient-to-br from-purple-500 to-pink-500"
        },
        {
            title: "Human-in-the-Loop Safety",
            description: "When queries exceed AI capabilities, automatic ticket generation ensures seamless escalation to human agents. No customer is left behind.",
            icon: "🤝",
            gradient: "from-yellow-500 to-orange-500",
            color: "bg-gradient-to-br from-orange-500 to-red-500"

        }
    ];

    const industries = [
        {
            name: "E-Commerce & Retail",
            desc: "Order tracking, returns processing, inventory queries, and personalized shopping assistance",
            icon: "🛒",
            color: "bg-gradient-to-br from-blue-500 to-cyan-500"
        },
        {
            name: "SaaS & Subscriptions",
            desc: "Billing management, account provisioning, technical support, and feature guidance",
            icon: "💻",
            color: "bg-gradient-to-br from-purple-500 to-pink-500"
        },
        {
            name: "Telecommunications",
            desc: "Network diagnostics, service provisioning, outage resolution, and plan optimization",
            icon: "📡",
            color: "bg-gradient-to-br from-orange-500 to-red-500"
        }
    ];

    const testimonials = [
        {
            quote: "Response times dropped from 2 hours to 3 minutes. Our customers love the instant resolutions.",
            author: "Sarah Chen",
            role: "Head of Customer Success",
            company: "TechRetail Inc."
        },
        {
            quote: "Payment recovery increased by 45% in the first month. The ROI is phenomenal.",
            author: "Michael Rodriguez",
            role: "CFO",
            company: "SubscribeNow"
        },
        {
            quote: "Technical support tickets reduced by 70%. Our team can now focus on complex issues.",
            author: "Priya Sharma",
            role: "VP Operations",
            company: "ConnectTel"
        }
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
            {/* Navigation */}
            
            {/* Hero Section */}
            <section className="pt-24 sm:pt-28 lg:pt-32 pb-12 sm:pb-16 lg:pb-20 px-4 sm:px-6">
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-12 sm:mb-16">
                        <div className="inline-block mb-4 sm:mb-6 px-4 sm:px-6 py-2 sm:py-3 bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-700 rounded-full text-xs sm:text-sm font-semibold shadow-md">
                            <span className="text-sm sm:text-base">✨</span> Next-Generation AI Customer Support
                        </div>
                        <h2 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold text-gray-900 mb-4 sm:mb-6 lg:mb-8 leading-tight px-4">
                            Transform Support Into<br />
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 animate-gradient">
                                Instant Resolutions
                            </span>
                        </h2>
                        <p className="text-base sm:text-lg md:text-xl lg:text-2xl text-gray-600 max-w-4xl mx-auto mb-8 sm:mb-10 lg:mb-12 leading-relaxed px-4">
                            Powered by LangChain and MongoDB, our agentic AI system autonomously handles complex workflows—from order verification to payment recovery to technical troubleshooting.
                        </p>
                        <div className="flex flex-col sm:flex-row justify-center gap-3 sm:gap-4 mb-6 sm:mb-8 px-4">
                            <Link to={isAuthenticated ? `/chat/${user?.customer_id}` : "/signIn"} className="px-6 sm:px-8 lg:px-10 py-3 sm:py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-base sm:text-lg font-semibold rounded-full shadow-2xl hover:shadow-blue-500/50 transition transform hover:scale-105 flex items-center justify-center gap-2">
                                <span className="text-xl sm:text-2xl">💬</span> {isAuthenticated ? 'Open Support Chat' : 'Sign In to Chat'}
                            </Link>
                            <button className="px-6 sm:px-8 lg:px-10 py-3 sm:py-4 bg-white text-gray-700 text-base sm:text-lg font-semibold rounded-full shadow-xl hover:shadow-2xl transition border-2 border-gray-200 hover:border-blue-400">
                                Watch Demo →
                            </button>
                        </div>
                        <p className="text-xs sm:text-sm text-gray-500 px-4">
                            <span className="text-sm sm:text-base">🔒</span> No credit card required • <span className="text-sm sm:text-base">⚡</span> Setup in 5 minutes
                        </p>
                    </div>

                    {/* Animated Stats */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4 lg:gap-6 max-w-6xl mx-auto mt-12 sm:mt-16 lg:mt-20 px-4">
                        {[
                            { value: "95%", label: "Resolution Rate", icon: "✅" },
                            { value: "3min", label: "Avg Response Time", icon: "⚡" },
                            { value: "24/7", label: "Always Available", icon: "🌍" },
                            { value: "70%", label: "Cost Reduction", icon: "💰" }
                        ].map((stat, idx) => (
                            <div key={idx} className="text-center p-4 sm:p-6 lg:p-8 bg-white rounded-xl sm:rounded-2xl shadow-xl hover:shadow-2xl transition transform hover:scale-105 border border-gray-100">
                                <div className="text-2xl sm:text-3xl lg:text-4xl mb-2 sm:mb-3">{stat.icon}</div>
                                <div className="text-2xl sm:text-3xl lg:text-4xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-1 sm:mb-2">
                                    {stat.value}
                                </div>
                                <div className="text-xs sm:text-sm font-medium text-gray-600">{stat.label}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section id="features" className="py-16 sm:py-20 lg:py-24 bg-linear-to-br from-gray-50 to-blue-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6">
                    <div className="text-center mb-12 sm:mb-16 lg:mb-20">
                        <div className="inline-block mb-3 sm:mb-4 px-4 sm:px-6 py-1.5 sm:py-2 bg-blue-100 text-blue-700 rounded-full text-xs sm:text-sm font-semibold">
                            <span className="text-sm sm:text-base">🚀</span> Powerful Capabilities
                        </div>
                        <h3 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 mb-4 sm:mb-6 px-4">Intelligent Workflows That Work</h3>
                        <p className="text-base sm:text-lg lg:text-xl text-gray-600 max-w-3xl mx-auto px-4">
                            Autonomous agents that understand, decide, and act on complex customer issues
                        </p>
                    </div>
                    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 lg:gap-8">
                        {features.map((feature, idx) => (
                            <div key={idx} className="group relative overflow-hidden bg-white p-6 sm:p-8 lg:p-10 rounded-2xl sm:rounded-3xl shadow-xl hover:shadow-2xl transition-all duration-300 border-2 border-transparent hover:border-blue-400">
                                <div className={`absolute top-0 right-0 w-24 h-24 sm:w-32 sm:h-32 ${feature.color} opacity-10 rounded-full -mr-12 sm:-mr-16 -mt-12 sm:-mt-16 group-hover:scale-150 transition-transform duration-500`}></div>
                                <div className={`inline-block p-3 sm:p-4 rounded-xl sm:rounded-2xl bg-gradient-to-br ${feature.gradient} mb-4 sm:mb-6`}>
                                    <div className="text-3xl sm:text-4xl lg:text-5xl">{feature.icon}</div>
                                </div>
                                <h4 className="text-lg sm:text-xl lg:text-2xl font-bold text-gray-900 mb-3 sm:mb-4">{feature.title}</h4>
                                <p className="text-sm sm:text-base text-gray-600 leading-relaxed">{feature.description}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Industries Section */}
            <section id="industries" className="py-16 sm:py-20 lg:py-24">
                <div className="max-w-7xl mx-auto px-4 sm:px-6">
                    <div className="text-center mb-12 sm:mb-16 lg:mb-20">
                        <div className="inline-block mb-3 sm:mb-4 px-4 sm:px-6 py-1.5 sm:py-2 bg-purple-100 text-purple-700 rounded-full text-xs sm:text-sm font-semibold">
                            <span className="text-sm sm:text-base">🏢</span> Industry Solutions
                        </div>
                        <h3 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 mb-4 sm:mb-6 px-4">Built for Every Business</h3>
                        <p className="text-base sm:text-lg lg:text-xl text-gray-600 max-w-3xl mx-auto px-4">
                            Adaptable AI solutions tailored to your industry's unique challenges
                        </p>
                    </div>
                    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 lg:gap-8">
                        {industries.map((industry, idx) => (
                            <div key={idx} className="group relative overflow-hidden bg-white p-6 sm:p-8 lg:p-10 rounded-2xl sm:rounded-3xl shadow-xl hover:shadow-2xl transition-all duration-300 border-2 border-transparent hover:border-blue-400">
                                <div className={`absolute top-0 right-0 w-24 h-24 sm:w-32 sm:h-32 ${industry.color} opacity-10 rounded-full -mr-12 sm:-mr-16 -mt-12 sm:-mt-16 group-hover:scale-150 transition-transform duration-500`}></div>
                                <div className="relative">
                                    <div className="text-4xl sm:text-5xl lg:text-6xl mb-4 sm:mb-6">{industry.icon}</div>
                                    <h4 className="text-lg sm:text-xl lg:text-2xl font-bold text-gray-900 mb-3 sm:mb-4">{industry.name}</h4>
                                    <p className="text-sm sm:text-base text-gray-600 leading-relaxed">{industry.desc}</p>
                                    <button className="mt-4 sm:mt-6 text-sm sm:text-base text-blue-600 font-semibold hover:text-blue-700 transition">
                                        Learn More →
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Testimonials Section */}
            <section id="testimonials" className="py-16 sm:py-20 lg:py-24 bg-gradient-to-br from-blue-600 to-indigo-700">
                <div className="max-w-7xl mx-auto px-4 sm:px-6">
                    <div className="text-center mb-12 sm:mb-16">
                        <div className=" inline-block mb-3 sm:mb-4 px-4 sm:px-6 py-1.5 sm:py-2 bg-white/20  text-white rounded-full text-xs sm:text-sm font-semibold">
                            <span className="text-sm sm:text-base">💬</span> Customer Stories
                        </div>
                        <h3 className="text-3xl sm:text-4xl lg:text-4.5xl font-bold text-white mb-4 sm:mb-6 px-4">Loved by Teams Worldwide</h3>
                        <p className="text-base sm:text-lg text-blue-100 px-4">
                            See how leading companies transform their support operations
                        </p>
                    </div>
                    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 lg:gap-8">
                        {testimonials.map((testimonial, idx) => (
                            <div key={idx} className="bg-white/10  backdrop-blur-lg p-6 sm:p-8 rounded-2xl sm:rounded-3xl border border-white/20  hover:bg-opacity-20 transition">
                                <div className="text-yellow-400 text-xl sm:text-2xl lg:text-3xl mb-3 sm:mb-4">⭐⭐⭐⭐⭐</div>
                                <p className="text-white text-sm sm:text-base lg:text-base mb-4 sm:mb-6 leading-relaxed italic">"{testimonial.quote}"</p>
                                <div className="border-t border-white/20 pt-3 sm:pt-4">
                                    <p className="text-white font-bold text-sm sm:text-base">{testimonial.author}</p>
                                    <p className="text-blue-200 text-xs sm:text-sm">{testimonial.role}</p>
                                    <p className="text-blue-300 text-xs sm:text-sm">{testimonial.company}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="py-16 sm:py-20 lg:py-24">
                <div className="max-w-5xl mx-auto px-4 sm:px-6">
                    <div className="relative overflow-hidden bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-600 rounded-2xl sm:rounded-3xl p-8 sm:p-12 lg:p-16 shadow-2xl">
                        <div className="absolute top-0 right-0 w-32 h-32 sm:w-48 sm:h-48 lg:w-64 lg:h-64 bg-white opacity-10 rounded-full -mr-16 sm:-mr-24 lg:-mr-32 -mt-16 sm:-mt-24 lg:-mt-32"></div>
                        <div className="absolute bottom-0 left-0 w-32 h-32 sm:w-48 sm:h-48 lg:w-64 lg:h-64 bg-white opacity-10 rounded-full -ml-16 sm:-ml-24 lg:-ml-32 -mb-16 sm:-mb-24 lg:-mb-32"></div>
                        <div className="relative text-center">
                            <h3 className="text-3xl sm:text-4xl lg:text-4.5xl font-bold text-white mb-4 sm:mb-6 px-4">Ready to Get Started?</h3>
                            <p className="text-lg sm:text-xl lg:text-1.5xl text-blue-100 mb-6 sm:mb-8 lg:mb-10 px-4">
                                Join thousands of businesses delivering exceptional customer experiences
                            </p>
                            <div className="flex flex-col sm:flex-row justify-center gap-3 sm:gap-4 mb-6 sm:mb-8 px-4">
                                <input
                                    type="email"
                                    placeholder="Enter your work email"
                                    className="bg-white px-6 sm:px-8 py-3 sm:py-4 rounded-full w-full sm:w-80 lg:w-96 text-gray-900 text-sm sm:text-base lg:text-lg focus:outline-none focus:ring-4 focus:ring-white shadow-xl"
                                />
                                <button className="px-6 sm:px-8 lg:px-10 py-3 sm:py-4 bg-white text-blue-600 text-sm sm:text-base lg:text-lg font-semibold rounded-full hover:bg-gray-100 transition transform hover:scale-105 shadow-xl whitespace-nowrap">
                                    Start Free Trial
                                </button>
                            </div>
                            <p className="text-blue-100 text-xs sm:text-sm px-4 flex justify-center gap-4">
                                <div>
                                    <span className="text-sm sm:text-base">✨</span> Free 14-day trial 
                                </div>
                                <div>
                                    <span className="text-sm sm:text-base">💳</span> No credit card required 
                                </div>
                                <div>
                                    <span className="text-sm sm:text-base">🚀</span> Setup in minutes
                                </div>
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="bg-gray-900 text-gray-400 py-12 sm:py-16">
                <div className="max-w-7xl mx-auto px-4 sm:px-6">
                    <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-8 sm:gap-10 lg:gap-12 mb-8 sm:mb-12">
                        <div className="sm:col-span-2">
                            <div className="flex items-center space-x-2 sm:space-x-3 mb-3 sm:mb-4">
                                <div className="text-2xl sm:text-3xl lg:text-4xl">🤖</div>
                                <h1 className="text-lg sm:text-xl lg:text-2xl font-bold text-white">AgenticAI Support</h1>
                            </div>
                            <p className="text-gray-400 text-sm sm:text-base mb-4 sm:mb-6 leading-relaxed">
                                Revolutionizing customer support with autonomous AI agents powered by LangChain and MongoDB.
                            </p>
                            <Link to={"/chat/newchat"} className="justify-self-start px-4 sm:px-6 py-2 sm:py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white text-sm sm:text-base font-semibold rounded-full hover:shadow-lg transition flex items-center gap-2">
                                <span className="text-base sm:text-lg">💬</span> Chat Now
                            </Link>
                        </div>
                        <div>
                            <h5 className="text-white font-bold mb-3 sm:mb-4 text-sm sm:text-base">Product</h5>
                            <ul className="space-y-2 sm:space-y-3 text-xs sm:text-sm">
                                <li><a href="#" className="hover:text-white transition">Features</a></li>
                                <li><a href="#" className="hover:text-white transition">Industries</a></li>
                                <li><a href="#" className="hover:text-white transition">Pricing</a></li>
                                <li><a href="#" className="hover:text-white transition">Documentation</a></li>
                            </ul>
                        </div>
                        <div>
                            <h5 className="text-white font-bold mb-3 sm:mb-4 text-sm sm:text-base">Company</h5>
                            <ul className="space-y-2 sm:space-y-3 text-xs sm:text-sm">
                                <li><a href="#" className="hover:text-white transition">About Us</a></li>
                                <li><a href="#" className="hover:text-white transition">Careers</a></li>
                                <li><a href="#" className="hover:text-white transition">Blog</a></li>
                                <li><a href="#" className="hover:text-white transition">Contact</a></li>
                            </ul>
                        </div>
                        <div>
                            <h5 className="text-white font-bold mb-3 sm:mb-4 text-sm sm:text-base">Support</h5>
                            <ul className="space-y-2 sm:space-y-3 text-xs sm:text-sm">
                                <li><a href="#" className="hover:text-white transition">Help Center</a></li>
                                <li><a href="#" className="hover:text-white transition">Privacy Policy</a></li>
                                <li><a href="#" className="hover:text-white transition">Terms of Service</a></li>
                                <li><a href="#" className="hover:text-white transition">Security</a></li>
                            </ul>
                        </div>
                    </div>
                    <div className="border-t border-gray-800 pt-6 sm:pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
                        <p className="text-xs sm:text-sm text-center md:text-left">© 2024 AgenticAI Support. All rights reserved.</p>
                        <div className="flex space-x-4 sm:space-x-6 text-xs sm:text-sm">
                            <a href="#" className="hover:text-white transition">Twitter</a>
                            <a href="#" className="hover:text-white transition">LinkedIn</a>
                            <a href="#" className="hover:text-white transition">GitHub</a>
                        </div>
                    </div>
                </div>
            </footer>

            {/* Floating Chat Button */}
            <Link to={"/chat/newchat"} className="fixed bottom-6 sm:bottom-8 right-6 sm:right-8 w-14 h-14 sm:w-16 sm:h-16 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-full shadow-2xl hover:shadow-blue-500/50 transition transform hover:scale-110 flex items-center justify-center text-2xl sm:text-3xl z-50">
                💬
            </Link>
        </div>
    );
}