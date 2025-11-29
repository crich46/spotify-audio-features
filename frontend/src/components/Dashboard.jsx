import React, { useState } from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import { Upload, Music, Activity, Zap, Heart, Smile, Mic } from 'lucide-react';

const Dashboard = () => {
    const [file, setFile] = useState(null);
    const [features, setFeatures] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
        setFeatures(null);
        setError(null);
    };

    const analyzeAudio = async () => {
        if (!file) return;
        setLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://localhost:8000/analyze', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Analysis failed');
            }

            const data = await response.json();
            setFeatures(data.features);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const data = features ? [
        { subject: 'Energy', A: features.energy, fullMark: 1 },
        { subject: 'Danceability', A: features.danceability, fullMark: 1 },
        { subject: 'Acousticness', A: features.acousticness, fullMark: 1 },
        { subject: 'Valence', A: features.valence, fullMark: 1 },
        { subject: 'Tempo (Norm)', A: Math.min(features.tempo / 200, 1), fullMark: 1 },
    ] : [];

    return (
        <div className="min-h-screen bg-gray-900 text-white p-8 font-sans selection:bg-green-500 selection:text-black">
            <div className="max-w-4xl mx-auto">
                <header className="mb-12 text-center">
                    <h1 className="text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-green-400 to-blue-500 mb-4">
                        Audio Vibe Analyzer
                    </h1>
                    <p className="text-gray-400 text-lg">Unlock the hidden features of your music.</p>
                </header>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {/* Upload Section */}
                    <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-8 border border-gray-700 shadow-xl flex flex-col items-center justify-center">
                        <div className="w-full h-64 border-2 border-dashed border-gray-600 rounded-xl flex flex-col items-center justify-center hover:border-green-500 transition-colors cursor-pointer relative group">
                            <input
                                type="file"
                                accept="audio/*"
                                onChange={handleFileChange}
                                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                            />
                            <Upload className="w-16 h-16 text-gray-500 group-hover:text-green-400 transition-colors mb-4" />
                            <p className="text-gray-400 group-hover:text-white transition-colors">
                                {file ? file.name : "Drag & Drop or Click to Upload"}
                            </p>
                        </div>

                        <button
                            onClick={analyzeAudio}
                            disabled={!file || loading}
                            className={`mt-6 w-full py-4 rounded-xl font-bold text-lg transition-all transform hover:scale-105 ${!file || loading
                                    ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                                    : 'bg-gradient-to-r from-green-500 to-emerald-600 text-black shadow-lg shadow-green-500/20'
                                }`}
                        >
                            {loading ? 'Analyzing...' : 'Analyze Track'}
                        </button>
                        {error && <p className="mt-4 text-red-400">{error}</p>}
                    </div>

                    {/* Visualization Section */}
                    <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-8 border border-gray-700 shadow-xl flex flex-col items-center justify-center relative overflow-hidden">
                        {!features ? (
                            <div className="text-center text-gray-500">
                                <Music className="w-24 h-24 mx-auto mb-4 opacity-20" />
                                <p>Upload a track to see its sonic fingerprint.</p>
                            </div>
                        ) : (
                            <div className="w-full h-full min-h-[300px]">
                                <ResponsiveContainer width="100%" height="100%">
                                    <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
                                        <PolarGrid stroke="#374151" />
                                        <PolarAngleAxis dataKey="subject" tick={{ fill: '#9CA3AF', fontSize: 12 }} />
                                        <PolarRadiusAxis angle={30} domain={[0, 1]} tick={false} axisLine={false} />
                                        <Radar
                                            name="Audio Features"
                                            dataKey="A"
                                            stroke="#10B981"
                                            strokeWidth={3}
                                            fill="#10B981"
                                            fillOpacity={0.3}
                                        />
                                    </RadarChart>
                                </ResponsiveContainer>

                                <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                                    <div className="flex items-center gap-2 text-gray-300">
                                        <Zap className="w-4 h-4 text-yellow-400" /> Energy: {features.energy.toFixed(2)}
                                    </div>
                                    <div className="flex items-center gap-2 text-gray-300">
                                        <Activity className="w-4 h-4 text-blue-400" /> Tempo: {features.tempo.toFixed(0)} BPM
                                    </div>
                                    <div className="flex items-center gap-2 text-gray-300">
                                        <Smile className="w-4 h-4 text-pink-400" /> Valence: {features.valence.toFixed(2)}
                                    </div>
                                    <div className="flex items-center gap-2 text-gray-300">
                                        <Mic className="w-4 h-4 text-purple-400" /> Acoustic: {features.acousticness.toFixed(2)}
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
