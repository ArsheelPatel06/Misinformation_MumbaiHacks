import React from 'react';
import { Clock, CheckCircle, AlertTriangle, FileText, Video, Link as LinkIcon, Search, ArrowRight } from 'lucide-react';

const HistoryPage = () => {
    const history = [
        {
            id: 1,
            type: 'Deepfake',
            name: 'interview_clip_v2.mp4',
            date: '2 hours ago',
            result: 'Authentic',
            confidence: '98%',
            icon: <Video className="w-5 h-5 text-blue-400" />
        },
        {
            id: 2,
            type: 'News',
            name: 'Breaking: Market Crash Rumors',
            date: '5 hours ago',
            result: 'Fake News',
            confidence: '92%',
            icon: <FileText className="w-5 h-5 text-purple-400" />
        },
        {
            id: 3,
            type: 'URL',
            name: 'https://suspicious-news.site/article',
            date: '1 day ago',
            result: 'Malicious',
            confidence: '99%',
            icon: <LinkIcon className="w-5 h-5 text-orange-400" />
        },
        {
            id: 4,
            type: 'Content',
            name: 'Viral Tweet Analysis',
            date: '2 days ago',
            result: 'Misleading',
            confidence: '85%',
            icon: <Search className="w-5 h-5 text-pink-400" />
        }
    ];

    return (
        <div className="max-w-5xl mx-auto">
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2">Verification History</h1>
                    <p className="text-gray-400">View and manage your past verification results.</p>
                </div>
                <button className="px-4 py-2 bg-white/5 hover:bg-white/10 text-white rounded-lg text-sm font-medium transition-colors">
                    Clear History
                </button>
            </div>

            <div className="space-y-4">
                {history.map((item) => (
                    <div key={item.id} className="bg-[#111] border border-white/10 rounded-xl p-4 flex items-center gap-6 hover:border-white/20 transition-all group">
                        <div className="p-3 bg-white/5 rounded-lg">
                            {item.icon}
                        </div>

                        <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-3 mb-1">
                                <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">{item.type}</span>
                                <span className="text-xs text-gray-600 flex items-center gap-1">
                                    <Clock className="w-3 h-3" /> {item.date}
                                </span>
                            </div>
                            <h3 className="text-white font-medium truncate group-hover:text-primary transition-colors">
                                {item.name}
                            </h3>
                        </div>

                        <div className="flex items-center gap-6">
                            <div className="text-right">
                                <div className={`text-sm font-bold ${item.result === 'Authentic' ? 'text-green-500' :
                                        item.result === 'Fake News' || item.result === 'Malicious' ? 'text-red-500' :
                                            'text-yellow-500'
                                    }`}>
                                    {item.result}
                                </div>
                                <div className="text-xs text-gray-500">{item.confidence} Confidence</div>
                            </div>

                            <button className="p-2 hover:bg-white/10 rounded-full text-gray-400 hover:text-white transition-colors">
                                <ArrowRight className="w-5 h-5" />
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default HistoryPage;
