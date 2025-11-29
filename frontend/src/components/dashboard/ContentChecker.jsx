import React, { useState } from 'react';
import { Search, Link as LinkIcon, Share2, AlertCircle, CheckCircle, Loader2, Twitter, Facebook, Instagram, Youtube } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const ContentChecker = () => {
    const [inputUrl, setInputUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);

    const handleVerify = async () => {
        if (!inputUrl) return;
        setLoading(true);
        setResult(null);

        try {
            const payload = {
                text: `Verify this social media post: ${inputUrl}`,
                audience_level: 'general'
            };

            const response = await fetch('http://localhost:8000/api/verify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            if (response.ok) {
                const data = await response.json();
                setResult({
                    rating: data.verdict === 'true' ? 'Authentic' : data.verdict === 'false' ? 'Fake/Misleading' : 'Unverified',
                    explanation: data.explanation.summary,
                    platform: 'Social Media'
                });
            } else {
                throw new Error('Verification failed');
            }
        } catch (error) {
            console.error(error);
            setResult({
                rating: 'Error',
                explanation: 'Failed to verify content. Please try again later.',
                platform: 'Social Media'
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto space-y-12">

            <div className="text-center space-y-6">
                <div>
                    <h1 className="text-4xl font-bold text-white mb-3">Content Checker</h1>
                    <p className="text-gray-400 text-lg">Verify posts, tweets, and media from social platforms.</p>
                </div>

                <div className="bg-[#111] border border-white/10 rounded-2xl p-8">
                    <div className="relative">
                        <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
                            <LinkIcon className="w-5 h-5 text-gray-500" />
                        </div>
                        <input
                            type="url"
                            value={inputUrl}
                            onChange={(e) => setInputUrl(e.target.value)}
                            placeholder="Paste social media link (Twitter, Facebook, Instagram, TikTok)..."
                            className="w-full bg-black/20 border border-white/10 rounded-xl py-4 pl-12 pr-32 text-white placeholder:text-gray-600 focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all text-lg"
                        />
                        <button
                            onClick={handleVerify}
                            disabled={loading || !inputUrl}
                            className="absolute right-2 top-2 bottom-2 px-6 bg-primary hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg font-bold transition-all flex items-center gap-2"
                        >
                            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                            Check
                        </button>
                    </div>

                    <div className="mt-6 flex items-center justify-center gap-6 text-gray-500 text-sm">
                        <span className="flex items-center gap-2"><Twitter className="w-4 h-4" /> Twitter/X</span>
                        <span className="flex items-center gap-2"><Facebook className="w-4 h-4" /> Facebook</span>
                        <span className="flex items-center gap-2"><Instagram className="w-4 h-4" /> Instagram</span>
                    </div>
                </div>
            </div>

            <AnimatePresence>
                {result && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="bg-white/5 border border-white/10 rounded-2xl p-8"
                    >
                        <div className="flex items-start gap-6">
                            <div className="p-4 rounded-full bg-yellow-500/20 text-yellow-500">
                                <AlertCircle className="w-8 h-8" />
                            </div>
                            <div className="flex-1">
                                <h3 className="text-2xl font-bold text-white mb-2">
                                    Result: <span className="text-yellow-500">{result.rating}</span>
                                </h3>
                                <p className="text-gray-300 leading-relaxed">{result.explanation}</p>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            <div className="grid md:grid-cols-2 gap-6">
                <div className="p-6 rounded-2xl bg-white/5 border border-white/10">
                    <Share2 className="w-8 h-8 text-secondary mb-4" />
                    <h3 className="text-xl font-bold text-white mb-2">Viral Content Analysis</h3>
                    <p className="text-gray-400">Analyze viral posts for coordinated bot activity and manipulation patterns.</p>
                </div>
                <div className="p-6 rounded-2xl bg-white/5 border border-white/10">
                    <AlertCircle className="w-8 h-8 text-accent mb-4" />
                    <h3 className="text-xl font-bold text-white mb-2">Source Credibility</h3>
                    <p className="text-gray-400">Check the history and reliability score of the account posting the content.</p>
                </div>
            </div>
        </div>
    );
};

export default ContentChecker;
