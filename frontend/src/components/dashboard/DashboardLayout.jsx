import React, { useState } from 'react';
import { Link, useLocation, Outlet } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
    Shield, ChevronDown, Settings, LogOut, User,
    FileVideo, Newspaper, FileText, Link as LinkIcon, Youtube, History,
    Menu, X, Search
} from 'lucide-react';

const DashboardLayout = () => {
    const [isToolsOpen, setIsToolsOpen] = useState(false);
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);
    const location = useLocation();

    const isActive = (path) => location.pathname.includes(path);

    const navLinks = [
        { name: 'Deepfake Verifier', path: '/dashboard/deepfake', icon: <FileVideo className="w-4 h-4" /> },
        { name: 'News Verifier', path: '/dashboard/news', icon: <Newspaper className="w-4 h-4" /> },
        { name: 'Content Checker', path: '/dashboard/content', icon: <Search className="w-4 h-4" /> },
    ];

    const toolsLinks = [
        { name: 'Text Verifier', path: '/dashboard/tools/text', icon: <FileText className="w-4 h-4" /> },
        { name: 'Article Verifier', path: '/dashboard/tools/article', icon: <Newspaper className="w-4 h-4" /> },
        { name: 'URL Verifier', path: '/dashboard/tools/url', icon: <LinkIcon className="w-4 h-4" /> },
        { name: 'YouTube Checker', path: '/dashboard/tools/youtube', icon: <Youtube className="w-4 h-4" /> },
        { name: 'History', path: '/dashboard/history', icon: <History className="w-4 h-4" /> },
    ];

    return (
        <div className="min-h-screen bg-background text-white flex flex-col">
            {/* Top Navigation */}
            <nav className="sticky top-0 z-40 bg-background/80 backdrop-blur-md border-b border-white/10 px-6 py-3">
                <div className="max-w-7xl mx-auto flex items-center justify-between">
                    {/* Logo */}
                    <Link to="/" className="flex items-center gap-2 group">
                        <img src="/logo.png" alt="DeepCheck Logo" className="w-8 h-8 object-contain" />
                        <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
                            DeepCheck
                        </span>
                    </Link>

                    {/* Main Navigation */}
                    <div className="hidden md:flex items-center gap-1">
                        {navLinks.map((link) => (
                            <Link
                                key={link.path}
                                to={link.path}
                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${isActive(link.path)
                                    ? 'bg-white/10 text-white shadow-sm border border-white/5'
                                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                                    }`}
                            >
                                {link.icon}
                                {link.name}
                            </Link>
                        ))}

                        {/* Tools Dropdown */}
                        <div className="relative group">
                            <button
                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${location.pathname.includes('/tools') || location.pathname.includes('/history')
                                    ? 'bg-white/10 text-white'
                                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                                    }`}
                                onMouseEnter={() => setIsToolsOpen(true)}
                                onClick={() => setIsToolsOpen(!isToolsOpen)}
                            >
                                <Shield className="w-4 h-4" />
                                Tools
                                <ChevronDown className={`w-3 h-3 transition-transform ${isToolsOpen ? 'rotate-180' : ''}`} />
                            </button>

                            <AnimatePresence>
                                {isToolsOpen && (
                                    <motion.div
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        exit={{ opacity: 0, y: 10 }}
                                        transition={{ duration: 0.2 }}
                                        className="absolute top-full right-0 mt-2 w-56 bg-[#1a1a1a] border border-white/10 rounded-xl shadow-xl overflow-hidden z-50"
                                        onMouseLeave={() => setIsToolsOpen(false)}
                                    >
                                        <div className="p-2 space-y-1">
                                            {toolsLinks.map((tool) => (
                                                <Link
                                                    key={tool.path}
                                                    to={tool.path}
                                                    className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-gray-300 hover:bg-white/10 hover:text-white transition-colors"
                                                    onClick={() => setIsToolsOpen(false)}
                                                >
                                                    <div className="p-1.5 rounded-md bg-white/5 text-primary">
                                                        {tool.icon}
                                                    </div>
                                                    {tool.name}
                                                </Link>
                                            ))}
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    </div>

                    {/* Right Actions */}
                    <div className="flex items-center gap-4">
                        <button
                            className="p-2 rounded-full hover:bg-white/10 text-gray-400 hover:text-white transition-colors relative group"
                            onClick={() => setIsSettingsOpen(true)}
                            onMouseEnter={() => setIsSettingsOpen(true)}
                        >
                            <Settings className="w-5 h-5" />
                        </button>
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary to-secondary p-[1px]">
                            <div className="w-full h-full rounded-full bg-black flex items-center justify-center">
                                <User className="w-4 h-4 text-white" />
                            </div>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Main Content Area */}
            <main className="flex-1 max-w-7xl mx-auto w-full p-6 relative">
                <Outlet />
            </main>

            {/* Settings Sidebar (Right) */}
            <AnimatePresence>
                {isSettingsOpen && (
                    <>
                        {/* Backdrop */}
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
                            onClick={() => setIsSettingsOpen(false)}
                        />

                        {/* Sidebar */}
                        <motion.div
                            initial={{ x: '100%' }}
                            animate={{ x: 0 }}
                            exit={{ x: '100%' }}
                            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                            className="fixed top-0 right-0 h-full w-80 bg-[#111] border-l border-white/10 z-50 shadow-2xl flex flex-col"
                            onMouseLeave={() => setIsSettingsOpen(false)}
                        >
                            <div className="p-6 border-b border-white/10 flex items-center justify-between">
                                <h2 className="text-xl font-bold text-white">Settings</h2>
                                <button
                                    onClick={() => setIsSettingsOpen(false)}
                                    className="p-2 hover:bg-white/10 rounded-full transition-colors"
                                >
                                    <X className="w-5 h-5 text-gray-400" />
                                </button>
                            </div>

                            <div className="flex-1 p-6 space-y-6">
                                <div className="space-y-4">
                                    <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Account</h3>
                                    <button className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-white/5 hover:bg-white/10 transition-colors text-left">
                                        <User className="w-5 h-5 text-primary" />
                                        <div>
                                            <div className="text-white font-medium">Profile</div>
                                            <div className="text-xs text-gray-400">Manage your account</div>
                                        </div>
                                    </button>
                                </div>

                                <div className="space-y-4">
                                    <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Preferences</h3>
                                    <div className="flex items-center justify-between px-4 py-3 rounded-xl bg-white/5">
                                        <span className="text-gray-300">Dark Mode</span>
                                        <div className="w-10 h-6 bg-primary rounded-full relative">
                                            <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full" />
                                        </div>
                                    </div>
                                    <div className="flex items-center justify-between px-4 py-3 rounded-xl bg-white/5">
                                        <span className="text-gray-300">Notifications</span>
                                        <div className="w-10 h-6 bg-gray-700 rounded-full relative">
                                            <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full" />
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="p-6 border-t border-white/10">
                                <Link to="/signin">
                                    <button className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-red-500/10 text-red-500 hover:bg-red-500/20 transition-colors font-medium">
                                        <LogOut className="w-5 h-5" />
                                        Sign Out
                                    </button>
                                </Link>
                            </div>
                        </motion.div>
                    </>
                )}
            </AnimatePresence>
        </div>
    );
};

export default DashboardLayout;
