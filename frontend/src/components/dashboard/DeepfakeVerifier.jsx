import React, { useState, useRef } from 'react';
import { Upload, FileVideo, Image as ImageIcon, Loader2, AlertCircle, CheckCircle, XCircle, Shield } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const DeepfakeVerifier = () => {
    const [dragActive, setDragActive] = useState(false);
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const inputRef = useRef(null);

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    };

    const handleChange = (e) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            handleFile(e.target.files[0]);
        }
    };

    const onButtonClick = () => {
        inputRef.current.click();
    };

    const handleFile = async (selectedFile) => {
        setFile(selectedFile);
        setError(null);
        setResult(null);
        setLoading(true);

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            // 1. Upload File
            const uploadRes = await fetch('http://localhost:8000/api/deepfake/upload', {
                method: 'POST',
                body: formData,
            });

            if (!uploadRes.ok) throw new Error('Upload failed');
            const uploadData = await uploadRes.json();
            const mediaId = uploadData.media_id;

            // 2. Analyze File
            const analyzeRes = await fetch(`http://localhost:8000/api/deepfake/analyze/${mediaId}`, {
                method: 'POST',
            });

            if (!analyzeRes.ok) throw new Error('Analysis failed');
            const analyzeData = await analyzeRes.json();

            setResult(analyzeData);
        } catch (err) {
            console.error(err);
            setError(err.message || 'Something went wrong during analysis');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-[80vh] flex flex-col items-center justify-center max-w-5xl mx-auto px-4">

            {/* Header */}
            <div className="text-center mb-10">
                <h1 className="text-4xl font-bold text-white mb-3">Deepfake Verifier</h1>
                <p className="text-gray-400 text-lg">Upload videos or images to detect AI manipulation with high precision.</p>
            </div>

            {/* Upload Area */}
            <div className="w-full max-w-3xl">
                <motion.div
                    className={`relative border-2 border-dashed rounded-3xl p-16 text-center transition-all duration-300 ${dragActive ? 'border-primary bg-primary/10' : 'border-white/10 bg-white/5 hover:bg-white/10'
                        }`}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                    animate={{ scale: dragActive ? 1.02 : 1 }}
                >
                    <input
                        ref={inputRef}
                        type="file"
                        className="hidden"
                        onChange={handleChange}
                        accept="video/*,image/*"
                    />

                    <AnimatePresence mode="wait">
                        {loading ? (
                            <motion.div
                                key="loading"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                className="flex flex-col items-center"
                            >
                                <div className="relative w-24 h-24 mb-6">
                                    <div className="absolute inset-0 border-4 border-white/10 rounded-full"></div>
                                    <div className="absolute inset-0 border-4 border-primary rounded-full border-t-transparent animate-spin"></div>
                                    <Loader2 className="absolute inset-0 m-auto w-10 h-10 text-primary animate-pulse" />
                                </div>
                                <h3 className="text-2xl font-bold text-white mb-2">Analyzing Media...</h3>
                                <p className="text-gray-400">Scanning for artifacts and manipulation patterns</p>
                            </motion.div>
                        ) : result ? (
                            <motion.div
                                key="result"
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="flex flex-col items-center"
                            >
                                <div className={`w-24 h-24 rounded-full flex items-center justify-center mb-6 ${result.analysis.is_deepfake ? 'bg-red-500/20' : 'bg-green-500/20'
                                    }`}>
                                    {result.analysis.is_deepfake ? (
                                        <AlertCircle className="w-12 h-12 text-red-500" />
                                    ) : (
                                        <CheckCircle className="w-12 h-12 text-green-500" />
                                    )}
                                </div>

                                <h3 className="text-3xl font-bold text-white mb-2">
                                    {result.analysis.is_deepfake ? 'Deepfake Detected' : 'Likely Authentic'}
                                </h3>

                                <div className="bg-black/30 rounded-xl p-6 mt-6 w-full text-left">
                                    <div className="flex justify-between items-center mb-4">
                                        <span className="text-gray-400">Confidence Score</span>
                                        <span className={`text-xl font-bold ${result.analysis.confidence > 80 ? 'text-green-400' : 'text-yellow-400'
                                            }`}>
                                            {result.analysis.confidence}%
                                        </span>
                                    </div>
                                    <p className="text-gray-300 leading-relaxed">
                                        {result.analysis.explanation}
                                    </p>
                                </div>

                                <button
                                    onClick={() => { setResult(null); setFile(null); }}
                                    className="mt-8 px-8 py-3 bg-white/10 hover:bg-white/20 rounded-full text-white font-medium transition-colors"
                                >
                                    Analyze Another File
                                </button>
                            </motion.div>
                        ) : (
                            <motion.div
                                key="upload"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                            >
                                <div className="w-24 h-24 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-8 group-hover:scale-110 transition-transform duration-300">
                                    <Upload className="w-10 h-10 text-primary" />
                                </div>
                                <h3 className="text-2xl font-bold text-white mb-3">Drag & Drop or Click to Upload</h3>
                                <p className="text-gray-400 mb-10">Supports MP4, AVI, JPG, PNG (Max 500MB)</p>

                                <div className="flex justify-center gap-4">
                                    <button
                                        onClick={onButtonClick}
                                        className="px-8 py-3 bg-white/10 rounded-full text-sm font-bold hover:bg-white/20 transition-colors flex items-center gap-2 border border-white/5"
                                    >
                                        <FileVideo className="w-4 h-4" /> Upload Video
                                    </button>
                                    <button
                                        onClick={onButtonClick}
                                        className="px-8 py-3 bg-white/10 rounded-full text-sm font-bold hover:bg-white/20 transition-colors flex items-center gap-2 border border-white/5"
                                    >
                                        <ImageIcon className="w-4 h-4" /> Upload Image
                                    </button>
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {error && (
                        <div className="absolute bottom-4 left-0 right-0 mx-auto w-fit px-4 py-2 bg-red-500/20 border border-red-500/50 rounded-lg text-red-200 text-sm flex items-center gap-2">
                            <XCircle className="w-4 h-4" />
                            {error}
                        </div>
                    )}
                </motion.div>
            </div>

            {/* Relevant Content Below */}
            <div className="grid md:grid-cols-3 gap-6 w-full max-w-5xl mt-16">
                <InfoCard
                    icon={<Shield className="w-6 h-6 text-secondary" />}
                    title="Privacy First"
                    description="Your uploads are processed securely and automatically deleted after analysis."
                />
                <InfoCard
                    icon={<Loader2 className="w-6 h-6 text-primary" />}
                    title="Real-time Analysis"
                    description="Our advanced AI models analyze frame-by-frame artifacts in seconds."
                />
                <InfoCard
                    icon={<AlertCircle className="w-6 h-6 text-accent" />}
                    title="Detection Capabilities"
                    description="Detects face swapping, lip-sync manipulation, and generative AI artifacts."
                />
            </div>
        </div>
    );
};

const InfoCard = ({ icon, title, description }) => (
    <div className="p-6 rounded-2xl bg-white/5 border border-white/10 hover:border-white/20 transition-colors">
        <div className="mb-4 p-3 rounded-xl bg-white/5 w-fit">
            {icon}
        </div>
        <h3 className="text-lg font-bold text-white mb-2">{title}</h3>
        <p className="text-sm text-gray-400 leading-relaxed">{description}</p>
    </div>
);

export default DeepfakeVerifier;
