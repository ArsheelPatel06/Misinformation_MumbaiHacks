import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { FileText, Link as LinkIcon, Youtube, Search, ArrowRight, Loader2, CheckCircle, AlertTriangle, XCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const ToolsPage = () => {
    const { toolType } = useParams();
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);

    const tools = {
        text: {
            title: 'Text Verifier',
            description: 'Analyze text for AI generation patterns and factual accuracy.',
            icon: <FileText className="w-6 h-6 text-primary" />,
            placeholder: 'Paste the text you want to verify here...',
            inputType: 'textarea'
        },
        article: {
            title: 'Article Verifier',
            description: 'Verify the credibility and bias of news articles.',
            icon: <Search className="w-6 h-6 text-secondary" />,
            placeholder: 'Paste article URL...',
            inputType: 'url'
        },
        url: {
            title: 'URL Verifier',
            description: 'Check if a website is a known source of misinformation.',
            icon: <LinkIcon className="w-6 h-6 text-accent" />,
            placeholder: 'https://example.com',
            inputType: 'url'
        },
        youtube: {
            title: 'YouTube Checker',
            description: 'Analyze YouTube videos for deepfakes and misleading content.',
            icon: <Youtube className="w-6 h-6 text-red-500" />,
            placeholder: 'https://youtube.com/watch?v=...',
            inputType: 'url'
        }
    };

    const currentTool = tools[toolType] || tools.text;

    const handleVerify = async () => {
        if (!input) return;
        setLoading(true);
        setResult(null);

        try {
            let textToVerify = input;
            if (toolType === 'article') textToVerify = `Verify this article: ${input}`;
            else if (toolType === 'url') textToVerify = `Verify this website: ${input}`;
            else if (toolType === 'youtube') textToVerify = `Verify this YouTube video: ${input}`;

            const payload = {
                text: textToVerify,
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
                    status: data.verdict === 'true' ? 'Verified' : data.verdict === 'false' ? 'False' : 'Uncertain',
                    score: Math.round(data.credibility_score * 100),
                    summary: data.explanation.summary,
                    details: [
                        `Confidence: ${Math.round(data.confidence * 100)}%`,
                        `Verdict: ${data.verdict}`,
                        `Sources: ${data.explanation.citations ? data.explanation.citations.length : 0}`
                    ]
                });
            } else {
                throw new Error('Verification failed');
            }
        } catch (error) {
            console.error(error);
            // Handle error
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto">
            <div className="mb-8 flex items-center gap-4">
                <div className="p-3 bg-white/5 rounded-xl border border-white/10">
                    {currentTool.icon}
                </div>
                <div>
                    <h1 className="text-3xl font-bold text-white mb-1">{currentTool.title}</h1>
                    <p className="text-gray-400">{currentTool.description}</p>
                </div>
            </div>

            <div className="bg-[#111] border border-white/10 rounded-2xl p-8 mb-8">
                <div className="relative">
                    {currentTool.inputType === 'textarea' ? (
                        <textarea
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder={currentTool.placeholder}
                            className="w-full h-48 bg-black/20 border border-white/10 rounded-xl p-4 text-white placeholder:text-gray-600 focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all resize-none"
                        />
                    ) : (
                        <div className="relative">
                            <input
                                type="url"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder={currentTool.placeholder}
                                className="w-full bg-black/20 border border-white/10 rounded-xl py-4 pl-4 pr-32 text-white placeholder:text-gray-600 focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all"
                            />
                        </div>
                    )}

                    <div className="mt-4 flex justify-end">
                        <button
                            onClick={handleVerify}
                            disabled={loading || !input}
                            className="px-8 py-3 bg-primary hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg font-bold transition-all flex items-center gap-2"
                        >
                            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Analyze'}
                        </button>
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
                            <div className="p-4 rounded-full bg-green-500/20 text-green-500">
                                <CheckCircle className="w-8 h-8" />
                            </div>
                            <div className="flex-1">
                                <div className="flex items-center justify-between mb-2">
                                    <h3 className="text-2xl font-bold text-white">Analysis Complete</h3>
                                    <span className="px-3 py-1 bg-green-500/10 text-green-500 rounded-full text-sm font-medium">
                                        {result.score}% Trust Score
                                    </span>
                                </div>
                                <p className="text-gray-300 leading-relaxed mb-6">{result.summary}</p>

                                <div className="grid md:grid-cols-3 gap-4">
                                    {result.details.map((detail, idx) => (
                                        <div key={idx} className="p-4 bg-black/20 rounded-xl border border-white/5 text-sm text-gray-400">
                                            {detail}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default ToolsPage;
