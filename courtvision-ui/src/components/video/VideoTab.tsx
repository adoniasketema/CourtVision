import { VideoPlayer } from './VideoPlayer';
import { EventsSidePanel } from './EventsSidePanel';
import { useStore } from '../../store/useStore';
import { Activity, Users } from 'lucide-react';

export function VideoTab() {
    const apiStats = useStore((state) => state.apiStats);
    const players = apiStats?.players || {};
    const playerIds = Object.keys(players);

    const team1Players = playerIds
        .filter((id) => players[id].team === 1)
        .sort((a, b) => players[b].distance_ft - players[a].distance_ft)
        .slice(0, 8);

    const team2Players = playerIds
        .filter((id) => players[id].team === 2)
        .sort((a, b) => players[b].distance_ft - players[a].distance_ft)
        .slice(0, 8);

    const maxDistance = Math.max(
        ...playerIds.map((id) => players[id].distance_ft),
        1
    );

    return (
        <div className="h-full flex gap-6 max-h-full">
            <div className="flex-1 flex flex-col min-w-0 overflow-y-auto custom-scrollbar pr-1">
                <div className="bg-charcoal-800 border border-charcoal-700 rounded-2xl overflow-hidden shadow-2xl relative aspect-video flex-shrink-0">
                    <VideoPlayer />
                </div>

                {/* Kinematic Exertion Leaderboard */}
                <div className="mt-6 flex-1 bg-charcoal-800 border border-charcoal-700 rounded-2xl p-6 shadow-xl flex flex-col">
                    <div className="flex items-center justify-between mb-4 border-b border-charcoal-700 pb-4">
                        <div className="flex items-center gap-2">
                            <Activity className="w-5 h-5 text-brand-light animate-pulse" />
                            <h3 className="font-bold text-lg tracking-tight">Kinematic Player Exertion</h3>
                        </div>
                        <span className="text-xs bg-brand/20 text-brand-light px-2.5 py-1 rounded-md font-semibold border border-brand/30">
                            Spatial Telemetry
                        </span>
                    </div>

                    {playerIds.length === 0 ? (
                        <div className="py-12 flex flex-col items-center justify-center text-center text-gray-500 flex-1">
                            <Users className="w-10 h-10 mb-3 text-charcoal-600 opacity-60" />
                            <p className="text-sm font-medium text-gray-400">
                                Player velocities &amp; cumulative travel distances will render automatically after analysis
                            </p>
                            <p className="text-xs text-charcoal-500 mt-1">
                                Calculated via bird&apos;s-eye homography perspective projections
                            </p>
                        </div>
                    ) : (
                        <div className="grid grid-cols-2 gap-6 pt-2">
                            {/* Team 1 Roster */}
                            <div className="bg-charcoal-900/60 border border-brand/20 rounded-xl p-4">
                                <div className="flex items-center gap-2 mb-4">
                                    <span className="w-2.5 h-2.5 rounded-full bg-brand-light shadow-[0_0_8px_rgba(110,140,255,0.8)]" />
                                    <span className="text-xs font-bold text-brand-light uppercase tracking-widest">
                                        Team 1 Leaderboard
                                    </span>
                                </div>
                                <div className="space-y-3">
                                    {team1Players.map((id) => {
                                        const dist = players[id].distance_ft;
                                        const pct = Math.min((dist / maxDistance) * 100, 100);
                                        return (
                                            <div key={id} className="text-xs">
                                                <div className="flex justify-between font-semibold mb-1">
                                                    <span className="text-gray-300">Player #{id}</span>
                                                    <span className="text-brand-light">{dist.toFixed(1)} ft</span>
                                                </div>
                                                <div className="w-full bg-charcoal-800 h-1.5 rounded-full overflow-hidden">
                                                    <div
                                                        className="bg-brand-light h-full rounded-full transition-all duration-500"
                                                        style={{ width: `${pct}%` }}
                                                    />
                                                </div>
                                            </div>
                                        );
                                    })}
                                    {team1Players.length === 0 && (
                                        <p className="text-xs text-gray-500 py-2 text-center">No track records</p>
                                    )}
                                </div>
                            </div>

                            {/* Team 2 Roster */}
                            <div className="bg-charcoal-900/60 border border-yellow-400/20 rounded-xl p-4">
                                <div className="flex items-center gap-2 mb-4">
                                    <span className="w-2.5 h-2.5 rounded-full bg-yellow-400 shadow-[0_0_8px_rgba(250,204,21,0.8)]" />
                                    <span className="text-xs font-bold text-yellow-400 uppercase tracking-widest">
                                        Team 2 Leaderboard
                                    </span>
                                </div>
                                <div className="space-y-3">
                                    {team2Players.map((id) => {
                                        const dist = players[id].distance_ft;
                                        const pct = Math.min((dist / maxDistance) * 100, 100);
                                        return (
                                            <div key={id} className="text-xs">
                                                <div className="flex justify-between font-semibold mb-1">
                                                    <span className="text-gray-300">Player #{id}</span>
                                                    <span className="text-yellow-400">{dist.toFixed(1)} ft</span>
                                                </div>
                                                <div className="w-full bg-charcoal-800 h-1.5 rounded-full overflow-hidden">
                                                    <div
                                                        className="bg-yellow-400 h-full rounded-full transition-all duration-500"
                                                        style={{ width: `${pct}%` }}
                                                    />
                                                </div>
                                            </div>
                                        );
                                    })}
                                    {team2Players.length === 0 && (
                                        <p className="text-xs text-gray-500 py-2 text-center">No track records</p>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            <div className="w-96 flex-shrink-0 flex flex-col bg-charcoal-800 border border-charcoal-700 rounded-2xl overflow-hidden shadow-xl">
                <div className="p-4 border-b border-charcoal-700 bg-charcoal-900/50">
                    <h2 className="font-bold text-lg tracking-tight">AI-Detected Events</h2>
                    <p className="text-xs text-brand-light mt-1 font-medium">Passes · Interceptions · Possession</p>
                </div>
                <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
                    <EventsSidePanel />
                </div>
            </div>
        </div>
    );
}
