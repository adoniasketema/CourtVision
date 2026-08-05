import { useRef, useEffect } from 'react';
import { useStore } from '../../store/useStore';

export function VideoPlayer() {
    const videoRef = useRef<HTMLVideoElement>(null);
    const seekTime = useStore((state) => state.seekTime);
    const setSeekTime = useStore((state) => state.setSeekTime);
    const outputVideoUrl = useStore((state) => state.outputVideoUrl);

    useEffect(() => {
        if (seekTime !== null && videoRef.current) {
            videoRef.current.currentTime = seekTime;
            videoRef.current.play().catch(e => console.log('Playback prevented', e));
            setSeekTime(null);
        }
    }, [seekTime, setSeekTime]);

    return (
        <div className="relative w-full h-full bg-black group">
            {/* Fallback shown behind video when src is not yet available */}
            <div className="absolute inset-0 bg-charcoal-900 border-2 border-charcoal-800 rounded-lg flex items-center justify-center -z-10">
                <span className="text-charcoal-600 font-bold text-2xl tracking-widest uppercase">Annotated Output</span>
            </div>

            <video
                ref={videoRef}
                className="w-full h-full object-cover"
                controls
                src={outputVideoUrl ?? undefined}
            >
                <track kind="captions" />
            </video>
        </div>
    );
}
