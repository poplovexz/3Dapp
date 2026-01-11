import { useState, ChangeEvent, useRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { CameraViz } from './components/CameraViz';
import { Loader2, Upload, RotateCcw, ImageIcon, Clapperboard, Play } from 'lucide-react';

function App() {
    const [azimuth, setAzimuth] = useState(0);
    const [elevation, setElevation] = useState(0);
    const [distance, setDistance] = useState(1);
    const [duration, setDuration] = useState(3); // Video duration
    const [bgStyle, setBgStyle] = useState("white_studio"); // Default to white for stability

    const [loading, setLoading] = useState(false);
    const [videoLoading, setVideoLoading] = useState(false);

    const [result, setResult] = useState<string | null>(null);
    const [videoResult, setVideoResult] = useState<string | null>(null);

    const [generatedPrompt, setGeneratedPrompt] = useState("");
    const [targetImage, setTargetImage] = useState<string | null>(null);

    const handleGenerate = async () => {
        setLoading(true);
        setResult(null);
        try {
            const response = await fetch('http://127.0.0.1:8000/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    azimuth, elevation, distance, image: targetImage, bg_style: bgStyle
                }),
            });
            const data = await response.json();
            setResult(data.result);
            setGeneratedPrompt(data.constructed_prompt);
        } catch (error) {
            console.error("Error generating:", error);
            setResult("Error generating content. Please verify backend is running.");
        } finally {
            setLoading(false);
        }
    };

    const handleGenerateVideo = async () => {
        setVideoLoading(true);
        setVideoResult(null);
        try {
            const response = await fetch('http://127.0.0.1:8000/generate-360', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    duration,
                    fps: 24,
                    elevation,
                    distance,
                    image: targetImage,
                    bg_style: bgStyle
                }),
            });
            const data = await response.json();
            setVideoResult(data.video_url); // Expect URL string
        } catch (error) {
            console.error("Error generating video:", error);
            alert("Video generation failed. Ensure backend is running.");
        } finally {
            setVideoLoading(false);
        }
    };

    const handleImageUpload = (event: ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onloadend = () => {
                setTargetImage(reader.result as string);
            };
            reader.readAsDataURL(file);
        }
    };

    return (
        <div className="flex h-screen bg-[#F5F5FA] text-gray-800 font-sans overflow-hidden">
            {/* Left Column: Input & Controls (Wider) */}
            <div className="flex-1 flex flex-col p-6 gap-4 overflow-y-auto max-w-[55%] border-r border-gray-200 bg-white">

                <div className="mb-2">
                    <h1 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                        <span className="text-2xl">🎬</span> Qwen Image Edit 2511 — 3D Control
                    </h1>
                    <p className="text-sm text-gray-500 mt-1">
                        Upload image, set angle, generated consistent characters.
                    </p>
                </div>

                {/* Input Image Area */}
                <div className="bg-slate-50 border-2 border-dashed border-slate-200 rounded-xl p-4 relative group hover:border-blue-400 transition-colors">
                    <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded flex items-center gap-1">
                            <ImageIcon size={14} /> Input Image
                        </span>
                        {targetImage && (
                            <button onClick={() => setTargetImage(null)} className="text-xs text-red-500 hover:underline">Clear</button>
                        )}
                    </div>

                    <div className="relative w-full aspect-[2/1] bg-white rounded-lg overflow-hidden flex flex-col items-center justify-center text-slate-400">
                        {targetImage ? (
                            <img src={targetImage} alt="Input" className="w-full h-full object-contain" />
                        ) : (
                            <div className="flex flex-col items-center gap-2">
                                <Upload size={32} />
                                <span className="text-sm">Drag & Drop or Click to Upload</span>
                            </div>
                        )}
                        <input
                            type="file"
                            accept="image/*"
                            onChange={handleImageUpload}
                            className="absolute inset-0 opacity-0 cursor-pointer"
                        />
                    </div>
                </div>

                {/* 3D Viewport */}
                <div className="bg-black rounded-xl overflow-hidden shadow-lg border border-gray-800 flex flex-col shrink-0 min-h-[300px]">
                    <div className="px-4 py-2 bg-gray-900 border-b border-gray-800 flex items-center justify-between">
                        <span className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                            🎮 3D View
                        </span>
                    </div>
                    <div className="flex-1 relative">
                        <Canvas camera={{ position: [5, 5, 5], fov: 50 }}>
                            <color attach="background" args={['#111']} />
                            <ambientLight intensity={0.5} />
                            <pointLight position={[10, 10, 10]} />
                            <CameraViz azimuth={azimuth} elevation={elevation} distance={distance} imageUrl={targetImage} />
                            <OrbitControls enablePan={false} minPolarAngle={0} maxPolarAngle={Math.PI / 1.5} />
                        </Canvas>
                        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-black/80 backdrop-blur border border-white/10 px-4 py-2 rounded-full text-xs font-mono text-green-400 whitespace-nowrap shadow-xl">
                            {generatedPrompt || "<sks> prompt preview"}
                        </div>
                    </div>
                </div>

                {/* Sliders */}
                <div className="bg-white rounded-xl border border-gray-200 p-4 space-y-4 shadow-sm">
                    <h3 className="text-sm font-bold text-gray-700 flex items-center gap-2">
                        🎚 Controls
                    </h3>

                    <div className="space-y-1">
                        <div className="flex justify-between text-xs font-medium text-gray-500">
                            <span className="text-blue-600">Azimuth</span>
                            <span>{azimuth}°</span>
                        </div>
                        <input type="range" min="0" max="360" value={azimuth} onChange={(e) => setAzimuth(Number(e.target.value))} className="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600" />
                    </div>

                    <div className="space-y-1">
                        <div className="flex justify-between text-xs font-medium text-gray-500">
                            <span className="text-purple-600">Elevation</span>
                            <span>{elevation}°</span>
                        </div>
                        <input type="range" min="-30" max="60" value={elevation} onChange={(e) => setElevation(Number(e.target.value))} className="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-purple-600" />
                    </div>

                    <div className="space-y-1">
                        <div className="flex justify-between text-xs font-medium text-gray-500">
                            <span className="text-amber-600">Distance</span>
                            <span>{distance.toFixed(1)}x</span>
                        </div>
                        <input type="range" min="0.5" max="2.0" step="0.1" value={distance} onChange={(e) => setDistance(Number(e.target.value))} className="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-amber-500" />
                    </div>

                    <div className="pt-2 border-t border-gray-100">
                        <label className="text-xs font-medium text-gray-500 mb-1 block">Background Style</label>
                        <select
                            value={bgStyle}
                            onChange={(e) => setBgStyle(e.target.value)}
                            className="w-full text-sm p-2 rounded-lg border border-gray-200 bg-gray-50 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
                        >
                            <option value="default">Default (AI Decision)</option>
                            <option value="white_studio">White Studio (Clean)</option>
                            <option value="green_screen">Green Screen (Chroma)</option>
                            <option value="dark_studio">Dark Studio (Mood)</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* Right Column: Output (Flexible) */}
            <div className="flex-1 flex flex-col p-6 bg-white gap-4 min-w-[300px]">

                {/* Generate Single Button */}
                <button
                    onClick={handleGenerate}
                    disabled={loading || videoLoading}
                    className="w-full py-4 bg-gradient-to-r from-[#6366f1] to-[#8b5cf6] hover:from-[#5558dd] hover:to-[#7c3aed] text-white rounded-xl font-bold text-lg shadow-lg shadow-indigo-500/20 disabled:opacity-70 disabled:grayscale transition-all flex items-center justify-center gap-2"
                >
                    {loading ? <Loader2 className="animate-spin" /> : "🚀 Generate Single Image"}
                </button>

                {/* Video Generation Section */}
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 flex flex-col gap-3">
                    <div className="flex justify-between items-center">
                        <h3 className="text-sm font-bold text-slate-700 flex items-center gap-2">
                            <Clapperboard size={16} className="text-rose-500" /> 360° Video Generation
                        </h3>
                        <span className="text-xs text-slate-400 bg-slate-200 px-2 py-1 rounded">24 FPS</span>
                    </div>

                    <div className="flex items-center gap-3">
                        <div className="flex-1">
                            <div className="flex justify-between text-xs text-slate-500 mb-1">
                                <span>Duration</span>
                                <span>{duration}s</span>
                            </div>
                            <input type="range" min="1" max="10" step="1" value={duration} onChange={(e) => setDuration(Number(e.target.value))} className="w-full h-1.5 bg-slate-200 rounded-lg accent-rose-500 cursor-pointer" />
                        </div>
                        <button
                            onClick={handleGenerateVideo}
                            disabled={loading || videoLoading}
                            className="px-4 py-2 bg-rose-500 hover:bg-rose-600 text-white rounded-lg text-sm font-bold shadow-md shadow-rose-200 disabled:opacity-50 transition-colors flex items-center gap-2 whitespace-nowrap"
                        >
                            {/* Wrap in spans to protect against external DOM manipulation (extensions) causing React insertBefore errors */}
                            <span>
                                {videoLoading ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} fill="currentColor" />}
                            </span>
                            <span>
                                {videoLoading ? "Rendering..." : "Generate Video"}
                            </span>
                        </button>
                    </div>
                    {videoLoading && <div className="text-[10px] text-rose-500 text-center animate-pulse">Rendering {duration * 24} frames... This may take a few minutes.</div>}
                </div>

                {/* Results Area */}
                <div className="flex-1 overflow-y-auto space-y-4">
                    {/* Image Result */}
                    <div className="bg-slate-50 border border-slate-200 rounded-xl p-1 min-h-[50%] flex flex-col">
                        <div className="px-3 py-2 border-b border-slate-200 text-sm font-semibold text-slate-600 flex justify-between">
                            <span>Generated Image</span>
                            {result && result.startsWith('data:image') && (
                                <a href={result} download={`generated_${Date.now()}.jpg`} className="text-xs text-blue-500 hover:underline">
                                    Download JPG
                                </a>
                            )}
                        </div>
                        <div className="flex-1 flex items-center justify-center bg-white m-1 rounded-lg border border-slate-100 overflow-hidden relative min-h-[200px]">
                            {result ? (
                                result.startsWith('data:image') ? (
                                    <img src={result} alt="Generated" className="w-full h-full object-contain" />
                                ) : (
                                    <div className="p-4 text-xs whitespace-pre-wrap">{result}</div>
                                )
                            ) : (
                                <div className="text-center text-slate-300">
                                    <span className="text-4xl">🖼️</span>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Video Result */}
                    {videoResult && (
                        <div className="bg-slate-50 border border-slate-200 rounded-xl p-1 flex flex-col animate-in fade-in slide-in-from-bottom-4">
                            <div className="px-3 py-2 border-b border-slate-200 text-sm font-semibold text-slate-600 flex justify-between">
                                <span>Generated Video</span>
                                <a href={videoResult} download className="text-xs text-blue-500 hover:underline">Download</a>
                            </div>
                            <div className="bg-black m-1 rounded-lg overflow-hidden flex items-center justify-center">
                                <video controls autoPlay loop src={videoResult} className="w-full max-h-[300px]" />
                            </div>
                        </div>
                    )}
                </div>

            </div>
        </div>
    );
}

export default App;
