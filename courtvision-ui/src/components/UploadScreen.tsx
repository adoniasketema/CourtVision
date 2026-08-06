import { useState, useEffect, useRef, useCallback } from 'react';
import { UploadCloud, CheckCircle2, Loader2, Video, AlertCircle } from 'lucide-react';
import { useStore } from '../store/useStore';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://20.69.120.68:8000';

const PROCESSING_MESSAGES = [
    "Uploading game video...",
    "Running YOLO detection...",
    "Tracking players...",
    "Assigning teams...",
    "Detecting possessions...",
    "Calculating stats...",
];

export function UploadScreen() {
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [isDragging, setIsDragging] = useState(false);
    const [processingStep, setProcessingStep] = useState(0);
    const [apiBase, setApiBase] = useState(() => {
        const stored = localStorage.getItem('courtvision_api_url') || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
        return stored.replace(/\/+$/, '').replace(/\/docs$/, '');
    });

    const handleApiChange = (url: string) => {
        const cleaned = url.replace(/\/+$/, '').replace(/\/docs$/, '');
        setApiBase(cleaned);
        localStorage.setItem('courtvision_api_url', cleaned);
    };
    const fileInputRef = useRef<HTMLInputElement>(null);
    const pollIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

    const uploadStatus = useStore(state => state.uploadStatus);
    const uploadError = useStore(state => state.uploadError);
    const setUploadStatus = useStore(state => state.setUploadStatus);
    const setUploadError = useStore(state => state.setUploadError);
    const setOutputVideoUrl = useStore(state => state.setOutputVideoUrl);
    const setApiStats = useStore(state => state.setApiStats);
    const setProcessingComplete = useStore(state => state.setProcessingComplete);

    // Advance the animated step indicator while processing
    useEffect(() => {
        if (uploadStatus !== 'processing') return;
        const timer = setInterval(() => {
            setProcessingStep(prev => Math.min(prev + 1, PROCESSING_MESSAGES.length - 1));
        }, 8000);
        return () => clearInterval(timer);
    }, [uploadStatus]);

    // Clean up polling on unmount
    useEffect(() => () => {
        if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    }, []);

    const startPolling = useCallback((jobId: string) => {
        setUploadStatus('processing');
        setProcessingStep(1);
        const cleanBase = apiBase.replace(/\/+$/, '').replace(/\/docs$/, '');

        pollIntervalRef.current = setInterval(async () => {
            try {
                const res = await fetch(`${cleanBase}/job/${jobId}`, {
                    headers: { 'ngrok-skip-browser-warning': '69420' }
                });
                if (!res.ok) throw new Error('Server error');
                const job = await res.json();

                if (job.status === 'done') {
                    clearInterval(pollIntervalRef.current!);
                    setOutputVideoUrl(`${cleanBase}/video/${job.output_filename}`);
                    setApiStats(job.stats);
                    
                    if (job.stats && job.stats.players) {
                        const mappedPlayers = Object.entries(job.stats.players).map(([id, data]: [string, any]) => ({
                            id,
                            name: `Player #${id}`,
                            teamId: data.team,
                            stats: { distanceFt: data.distance_ft }
                        }));
                        useStore.getState().setPlayers(mappedPlayers);
                    }

                    setUploadStatus('done');
                    setTimeout(() => setProcessingComplete(true), 400);
                } else if (job.status === 'error') {
                    clearInterval(pollIntervalRef.current!);
                    setUploadError(job.error || 'Processing failed');
                    setUploadStatus('error');
                }
            } catch {
                clearInterval(pollIntervalRef.current!);
                setUploadError('Lost connection to server');
                setUploadStatus('error');
            }
        }, 3000);
    }, [setUploadStatus, setUploadError, setOutputVideoUrl, setApiStats, setProcessingComplete, apiBase]);

    const handleUpload = async () => {
        if (!selectedFile) return;

        setUploadStatus('uploading');
        setUploadError(null);
        setProcessingStep(0);

        const formData = new FormData();
        formData.append('file', selectedFile);
        const cleanBase = apiBase.replace(/\/+$/, '').replace(/\/docs$/, '');

        try {
            const res = await fetch(`${cleanBase}/upload`, { 
                method: 'POST', 
                body: formData,
                headers: { 'ngrok-skip-browser-warning': '69420' }
            });
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || 'Upload failed');
            }
            const { job_id } = await res.json();
            startPolling(job_id);
        } catch (err) {
            setUploadError(err instanceof Error ? err.message : 'Upload failed');
            setUploadStatus('error');
        }
    };

    const handleFileSelect = (file: File) => {
        setSelectedFile(file);
        setUploadError(null);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        const file = e.dataTransfer.files[0];
        if (file) handleFileSelect(file);
    };

    const isProcessing = uploadStatus === 'uploading' || uploadStatus === 'processing';

    return (
        <div className="min-h-screen flex items-center justify-center p-6" style={{ background: 'var(--color-charcoal-950)' }}>
            <div className="w-full max-w-lg">
                <div className="text-center mb-10 text-brand font-bold text-3xl flex items-center justify-center gap-2">
                    <Video className="w-8 h-8" />
                    CourtVision AI
                </div>

                <div className="bg-charcoal-900 border border-charcoal-700 rounded-2xl p-8 shadow-2xl">
                    {!isProcessing ? (
                        <div className="flex flex-col items-center">
                            <div className="w-24 h-24 rounded-full bg-charcoal-800 flex items-center justify-center mb-6 border border-charcoal-700">
                                {uploadStatus === 'error' ? (
                                    <AlertCircle className="w-10 h-10 text-red-400" />
                                ) : (
                                    <UploadCloud className="w-10 h-10 text-brand-light" />
                                )}
                            </div>
                            <h2 className="text-2xl font-bold mb-2">Upload Game Video</h2>
                            <p className="text-gray-400 text-center mb-6 px-4">
                                Drag and drop your full game footage here. Our AI will automatically track players and extract stats.
                            </p>

                            <div className="w-full mb-6 bg-charcoal-950/80 p-4 rounded-xl border border-charcoal-700">
                                <label className="block text-xs font-semibold uppercase text-brand-light tracking-wider mb-2">
                                    🌐 Cloud AI Server Endpoint (Ngrok / Local)
                                </label>
                                <input
                                    type="text"
                                    value={apiBase}
                                    onChange={(e) => handleApiChange(e.target.value)}
                                    placeholder="e.g., https://abcd-12-34-56.ngrok-free.app"
                                    className="w-full bg-charcoal-900 text-gray-200 border border-charcoal-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-brand transition-colors"
                                />
                                <span className="text-[11px] text-gray-500 mt-1 block">
                                    Paste your live Google Colab Ngrok public link here!
                                </span>
                            </div>

                            {uploadError && (
                                <div className="w-full bg-red-500/10 border border-red-500/30 rounded-xl p-4 mb-4 text-red-400 text-sm font-medium">
                                    {uploadError}
                                </div>
                            )}

                            <div
                                onClick={() => fileInputRef.current?.click()}
                                onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                                onDragLeave={() => setIsDragging(false)}
                                onDrop={handleDrop}
                                className={`w-full border-2 border-dashed rounded-xl p-8 mb-6 flex flex-col items-center justify-center cursor-pointer bg-charcoal-950/50 transition-colors ${isDragging ? 'border-brand bg-charcoal-800' : 'border-charcoal-600 hover:border-brand hover:bg-charcoal-800'}`}
                            >
                                {selectedFile ? (
                                    <>
                                        <CheckCircle2 className="w-8 h-8 text-green-400 mb-2" />
                                        <span className="text-gray-200 font-medium text-sm truncate max-w-full px-2">{selectedFile.name}</span>
                                        <span className="text-gray-500 text-xs mt-1">{(selectedFile.size / 1024 / 1024).toFixed(1)} MB</span>
                                    </>
                                ) : (
                                    <span className="text-gray-500">Select .MP4 file or drop here</span>
                                )}
                            </div>
                            <input
                                ref={fileInputRef}
                                type="file"
                                accept="video/mp4,video/quicktime,video/x-msvideo"
                                className="hidden"
                                onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFileSelect(f); }}
                            />

                            <button
                                onClick={handleUpload}
                                disabled={!selectedFile}
                                className="w-full py-4 rounded-xl bg-brand hover:bg-brand-light text-white font-semibold transition-all shadow-lg active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                Start Processing
                            </button>
                        </div>
                    ) : (
                        <div className="py-8">
                            <h2 className="text-2xl font-bold mb-8 text-center text-gray-100">Processing Game...</h2>

                            <div className="space-y-4">
                                {PROCESSING_MESSAGES.map((msg, idx) => (
                                    <div key={idx} className={`flex items-center gap-4 p-4 rounded-lg transition-all duration-500 ${idx === processingStep ? 'bg-charcoal-800 border-l-4 border-brand' : 'opacity-40'}`}>
                                        {idx < processingStep ? (
                                            <CheckCircle2 className="w-6 h-6 text-green-400 flex-shrink-0" />
                                        ) : idx === processingStep ? (
                                            <Loader2 className="w-6 h-6 text-brand-light animate-spin flex-shrink-0" />
                                        ) : (
                                            <div className="w-6 h-6 rounded-full border-2 border-charcoal-600 flex-shrink-0" />
                                        )}
                                        <span className={`font-medium ${idx === processingStep ? 'text-white' : 'text-gray-400'}`}>
                                            {msg}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
