import { useState } from 'react';
import { useStore } from '../../store/useStore';
import { ArrowLeft, PlayCircle } from 'lucide-react';
import { StatCard } from './StatCard';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function PlayerProfile({ playerId }: { playerId: string }) {
    const [activeTab, setActiveTab] = useState<'stats' | 'clips'>('stats');

    const players = useStore((state) => state.players);
    const playerStats = useStore((state) => state.playerStats);
    const events = useStore((state) => state.events);
    const setSelectedPlayerId = useStore((state) => state.setSelectedPlayerId);
    const setSeekTime = useStore((state) => state.setSeekTime);
    const setCurrentTab = useStore((state) => state.setCurrentTab);

    const player = players.find(p => p.id === playerId);
    const stats = playerStats.find(s => s.playerId === playerId);
    const playerEvents = events.filter(e => e.playersInvolved.includes(playerId));

    if (!player || !stats) return null;

    const handleClipClick = (startTime: number) => {
        setSeekTime(startTime);
        setCurrentTab('video');
    };

    return (
        <div className="h-full flex flex-col pb-8">
            {/* Header */}
            <div className="mb-8 flex items-start justify-between">
                <div className="flex items-center gap-6">
                    <button
                        onClick={() => setSelectedPlayerId(null)}
                        className="w-10 h-10 rounded-full bg-charcoal-800 hover:bg-charcoal-700 border border-charcoal-700 flex items-center justify-center transition-colors text-white"
                    >
                        <ArrowLeft className="w-5 h-5" />
                    </button>

                    <div>
                        <div className="flex items-center gap-3 mb-1">
                            <span className="text-sm font-bold text-brand-light bg-brand/10 border border-brand/20 px-2 py-0.5 rounded tracking-widest">
                                #{player.jersey}
                            </span>
                            <span className="text-sm font-bold text-gray-400 tracking-widest uppercase">
                                {player.position}
                            </span>
                        </div>
                        <h2 className="text-3xl font-black text-white tracking-tight">{player.name}</h2>
                    </div>
                </div>

                {/* Sub-tabs */}
                <div className="flex bg-charcoal-800 border border-charcoal-700 rounded-lg p-1">
                    <button
                        onClick={() => setActiveTab('stats')}
                        className={twMerge(clsx("px-6 py-2 rounded-md text-sm font-bold transition-colors", activeTab === 'stats' ? "bg-charcoal-600 text-white shadow" : "text-gray-400 hover:text-white"))}
                    >
                        Stats
                    </button>
                    <button
                        onClick={() => setActiveTab('clips')}
                        className={twMerge(clsx("px-6 py-2 rounded-md text-sm font-bold transition-colors", activeTab === 'clips' ? "bg-brand text-white shadow" : "text-gray-400 hover:text-white"))}
                    >
                        Clips ({playerEvents.length})
                    </button>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto custom-scrollbar pr-4">
                {activeTab === 'stats' ? (
                    <div className="space-y-10">
                        <section>
                            <h3 className="text-lg font-bold border-b border-charcoal-700 pb-3 mb-5 text-gray-200 uppercase tracking-widest">Scoring Efficiency</h3>
                            <div className="grid grid-cols-2 md:grid-cols-4 xl:grid-cols-6 gap-4">
                                <StatCard label="PTS" value={stats.points} highlight />
                                <StatCard label="FGM/FGA" value={`${stats.FGM}/${stats.FGA}`} />
                                <StatCard label="3PM/3PA" value={`${stats.ThreePM}/${stats.ThreePA}`} />
                                <StatCard label="FTM/FTA" value={`${stats.FTM}/${stats.FTA}`} />
                                <StatCard label="eFG%" value={`${stats.eFG}%`} highlight />
                                <StatCard label="TS%" value={`${stats.TS}%`} />
                            </div>
                        </section>

                        <section>
                            <h3 className="text-lg font-bold border-b border-charcoal-700 pb-3 mb-5 text-gray-200 uppercase tracking-widest">Playmaking & Defense</h3>
                            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                                <StatCard label="AST" value={stats.assists} />
                                <StatCard label="REB" value={stats.rebounds} />
                                <StatCard label="STL" value={stats.steals} />
                                <StatCard label="BLK" value={stats.blocks} />
                                <StatCard label="TOV" value={stats.turnovers} />
                            </div>
                        </section>

                        <section>
                            <h3 className="text-lg font-bold border-b border-charcoal-700 pb-3 mb-5 text-gray-200 uppercase tracking-widest">Advanced Metrics</h3>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <StatCard label="MIN" value={stats.minutes} />
                                <StatCard label="+/-" value={stats.PlusMinus > 0 ? `+${stats.PlusMinus}` : stats.PlusMinus} highlight />
                                <StatCard label="ORtg" value={stats.ORtg} />
                                <StatCard label="DRtg" value={stats.DRtg} />
                                <StatCard label="Net Rtg" value={`+${stats.NetRating}`} highlight />
                                <StatCard label="PER" value={stats.PER} />
                                <StatCard label="Win Shares" value={stats.WinShares} />
                            </div>
                        </section>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {playerEvents.map(event => (
                            <button
                                key={event.id}
                                onClick={() => handleClipClick(event.startTime)}
                                className="group bg-charcoal-800 border border-charcoal-700 rounded-2xl overflow-hidden text-left hover:border-brand-light transition-colors shadow-lg"
                            >
                                <div className="aspect-video bg-charcoal-900 relative flex items-center justify-center border-b border-charcoal-700 overflow-hidden">
                                    <div className="absolute inset-0 bg-cover bg-center opacity-40 group-hover:opacity-60 transition-opacity" style={{ backgroundImage: "url('https://images.unsplash.com/photo-1546519638-68e109498ffc?q=80&w=2000&auto=format&fit=crop')" }}></div>
                                    <PlayCircle className="w-12 h-12 text-white/70 group-hover:text-brand-light group-hover:scale-110 transition-all z-10" />
                                    <div className="absolute bottom-3 right-3 bg-black/80 backdrop-blur text-white text-xs font-bold px-2 py-1 rounded">
                                        {event.endTime - event.startTime}s
                                    </div>
                                </div>
                                <div className="p-5">
                                    <div className="flex justify-between items-start mb-2">
                                        <span className="font-bold text-white capitalize text-lg">{event.type.replace('_', ' ')}</span>
                                        <span className="text-brand-light font-black">{event.points > 0 ? `+${event.points} PTS` : ''}</span>
                                    </div>
                                    <div className="text-sm text-gray-400 font-medium">
                                        Q{event.quarter} • {event.gameClock} • Score: {event.scoreAfter}
                                    </div>
                                </div>
                            </button>
                        ))}

                        {playerEvents.length === 0 && (
                            <div className="col-span-full py-20 text-center text-gray-500 font-medium">
                                No automated clips found for this player.
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
