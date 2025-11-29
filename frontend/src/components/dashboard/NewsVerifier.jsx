import React, { useState, useEffect } from 'react';
import { Search, Link as LinkIcon, FileText, ArrowRight, TrendingUp, AlertTriangle, CheckCircle, Clock, ExternalLink, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const NewsVerifier = () => {
    const [activeTab, setActiveTab] = useState('text'); // 'text' or 'url'
    const [inputText, setInputText] = useState('');
    const [inputUrl, setInputUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [verificationResult, setVerificationResult] = useState(null);
    const [trendingNews, setTrendingNews] = useState([]);
    const [trendingLoading, setTrendingLoading] = useState(true);

    // Fetch trending news on mount
    useEffect(() => {
        const fetchTrending = async () => {
            try {
                const response = await fetch('http://localhost:8000/api/trending');
                if (response.ok) {
                    const data = await response.json();
                    if (data && data.length > 0) {
                        setTrendingNews(data);
                    } else {
                        // Fallback mock data if API returns empty
                        setTrendingNews([
                            {
                                claim_text: "AI-generated images of politicians causing market crash",
                                rating: "False",
                                explanation: "No evidence supports this claim. Market movements were unrelated to deepfakes.",
                                source: "Reuters Fact Check"
                            },
                            {
                                claim_text: "New deepfake detection tool achieves 99% accuracy",
                                rating: "Unverified",
                                explanation: "Multiple startups claim this, but independent verification is pending.",
                                source: "TechCrunch"
                            },
                            {
                                claim_text: "Viral video of celebrity endorsing crypto scam is deepfake",
                                rating: "True",
                                explanation: "Visual artifacts and voice analysis confirm manipulation.",
                                source: "DeepCheck Analysis"
                            }
                        ]);
                    }
                }
            } catch (error) {
                console.error('Failed to fetch trending news:', error);
                // Fallback on error too
                setTrendingNews([
                    {
                        claim_text: "AI-generated images of politicians causing market crash",
                        rating: "False",
                        explanation: "No evidence supports this claim. Market movements were unrelated to deepfakes.",
                        source: "Reuters Fact Check"
                    },
                    {
                        claim_text: "New deepfake detection tool achieves 99% accuracy",
                        rating: "Unverified",
                        explanation: "Multiple startups claim this, but independent verification is pending.",
                        source: "TechCrunch"
                    },
                    {
                        claim_text: "Viral video of celebrity endorsing crypto scam is deepfake",
                        rating: "True",
                        explanation: "Visual artifacts and voice analysis confirm manipulation.",
                        source: "DeepCheck Analysis"
                    }
                ]);
            } finally {
                setTrendingLoading(false);
            }
        };

        fetchTrending();
    }, []);

    const handleVerify = async () => {
        if ((activeTab === 'text' && !inputText) || (activeTab === 'url' && !inputUrl)) return;

        setLoading(true);
        setVerificationResult(null);

        try {
            const payload = {
                text: activeTab === 'text' ? inputText : '',
                source_url: activeTab === 'url' ? inputUrl : null
            };

            // If URL mode, we might need to fetch content first or pass URL to backend
            // For now, assuming backend handles text verification primarily
            // If URL is provided but no text, we might need a different endpoint or logic
            // But let's try sending to /api/verify

            const response = await fetch('http://localhost:8000/api/verify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            if (response.ok) {
                const data = await response.json();
                setVerificationResult(data);
            } else {
                throw new Error('Verification failed');
            }
        } catch (error) {
            console.error(error);
            // Handle error state
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-6xl mx-auto space-y-12">

            {/* Header & Input Section */}
            <div className="text-center space-y-8">
                <div>
                    <h1 className="text-4xl font-bold text-white mb-3">News Verifier</h1>
                    <p className="text-gray-400 text-lg">Verify articles, claims, and URLs against trusted global sources.</p>
                </div>

                <div className="max-w-3xl mx-auto bg-[#111] border border-white/10 rounded-2xl p-2">
                    {/* Tabs */}
                    <div className="flex gap-2 mb-4 p-1 bg-black/20 rounded-xl">
                        <button
                            onClick={() => setActiveTab('text')}
                            className={`flex-1 py-3 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-2 ${activeTab === 'text' ? 'bg-white/10 text-white shadow-sm' : 'text-gray-400 hover:text-white'
                                }`}
                        >
                            <FileText className="w-4 h-4" /> Verify Text
                        </button>
                        <button
                            onClick={() => setActiveTab('url')}
                            className={`flex-1 py-3 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-2 ${activeTab === 'url' ? 'bg-white/10 text-white shadow-sm' : 'text-gray-400 hover:text-white'
                                }`}
                        >
                            <LinkIcon className="w-4 h-4" /> Verify URL
                        </button>
                    </div>

                    {/* Input Area */}
                    <div className="relative">
                        {activeTab === 'text' ? (
                            <textarea
                                value={inputText}
                                onChange={(e) => setInputText(e.target.value)}
                                placeholder="Paste the news text or claim here..."
                                className="w-full h-40 bg-transparent text-white p-4 rounded-xl resize-none focus:outline-none placeholder:text-gray-600"
                            />
                        ) : (
                            <div className="flex items-center px-4 h-40">
                                <input
                                    type="url"
                                    value={inputUrl}
                                    onChange={(e) => setInputUrl(e.target.value)}
                                    placeholder="https://example.com/news-article"
                                    className="w-full bg-transparent text-white text-lg focus:outline-none placeholder:text-gray-600"
                                />
                            </div>
                        )}

                        {/* Verify Button */}
                        <div className="absolute bottom-4 right-4">
                            <button
                                onClick={handleVerify}
                                disabled={loading || (activeTab === 'text' ? !inputText : !inputUrl)}
                                className="px-6 py-2 bg-primary hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-full font-bold transition-all flex items-center gap-2 shadow-lg shadow-primary/25"
                            >
                                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                                {loading ? 'Verifying...' : 'Verify Now'}
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Verification Result */}
            <AnimatePresence>
                {verificationResult && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="bg-white/5 border border-white/10 rounded-2xl p-8"
                    >
                        <div className="flex items-start gap-6">
                            <div className={`p-4 rounded-full ${verificationResult.rating === 'True' ? 'bg-green-500/20 text-green-500' :
                                verificationResult.rating === 'False' ? 'bg-red-500/20 text-red-500' :
                                    'bg-yellow-500/20 text-yellow-500'
                                }`}>
                                {verificationResult.rating === 'True' ? <CheckCircle className="w-8 h-8" /> :
                                    verificationResult.rating === 'False' ? <AlertTriangle className="w-8 h-8" /> :
                                        <TrendingUp className="w-8 h-8" />}
                            </div>
                            <div className="flex-1">
                                <h3 className="text-2xl font-bold text-white mb-2">
                                    Verdict: <span className={
                                        verificationResult.rating === 'True' ? 'text-green-500' :
                                            verificationResult.rating === 'False' ? 'text-red-500' :
                                                'text-yellow-500'
                                    }>{verificationResult.rating}</span>
                                </h3>
                                <p className="text-gray-300 leading-relaxed mb-6">{verificationResult.explanation}</p>

                                {verificationResult.sources && verificationResult.sources.length > 0 && (
                                    <div>
                                        <h4 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">Sources</h4>
                                        <div className="space-y-2">
                                            {verificationResult.sources.map((source, idx) => (
                                                <a key={idx} href={source.url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-primary hover:underline">
                                                    <ExternalLink className="w-4 h-4" />
                                                    {source.domain || source.url}
                                                </a>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Trending News Section */}
            <div>
                <div className="flex items-center justify-between mb-8">
                    <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                        <TrendingUp className="w-6 h-6 text-secondary" />
                        Trending Verification Requests
                    </h2>
                    <button className="text-sm text-gray-400 hover:text-white transition-colors flex items-center gap-1">
                        View All <ArrowRight className="w-4 h-4" />
                    </button>
                </div>

                {trendingLoading ? (
                    <div className="grid md:grid-cols-3 gap-6">
                        {[1, 2, 3].map((i) => (
                            <div key={i} className="h-64 bg-white/5 rounded-2xl animate-pulse" />
                        ))}
                    </div>
                ) : (
                    <div className="grid md:grid-cols-3 gap-6">
                        {trendingNews.length > 0 ? (
                            trendingNews.map((news, index) => (
                                <NewsCard key={index} news={news} />
                            ))
                        ) : (
                            <div className="col-span-3 text-center py-12 text-gray-500">
                                No trending news available at the moment.
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

const NewsCard = ({ news }) => (
    <div className="bg-[#111] border border-white/10 rounded-2xl overflow-hidden hover:border-white/20 transition-all group">
        <div className="p-6">
            <div className="flex items-center justify-between mb-4">
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${news.rating === 'False' ? 'bg-red-500/10 text-red-500' :
                    news.rating === 'True' ? 'bg-green-500/10 text-green-500' :
                        'bg-yellow-500/10 text-yellow-500'
                    }`}>
                    {news.rating || 'Unverified'}
                </span>
                <span className="text-xs text-gray-500 flex items-center gap-1">
                    <Clock className="w-3 h-3" /> 2h ago
                </span>
            </div>

            <h3 className="text-lg font-bold text-white mb-3 line-clamp-2 group-hover:text-primary transition-colors">
                {news.claim_text}
            </h3>

            <p className="text-gray-400 text-sm line-clamp-3 mb-4">
                {news.explanation || 'No explanation available.'}
            </p>

            <div className="flex items-center justify-between pt-4 border-t border-white/5">
                <span className="text-xs text-gray-500">Source: {news.source || 'Unknown'}</span>
                <button className="text-sm font-medium text-white hover:text-primary transition-colors flex items-center gap-1">
                    Read More <ArrowRight className="w-3 h-3" />
                </button>
            </div>
        </div>
    </div>
);

export default NewsVerifier;
