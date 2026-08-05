import { useStore } from '../../store/useStore';
import { PlayerCard } from './PlayerCard';
import { PlayerProfile } from './PlayerProfile';
import { StatCard } from './StatCard';
import { Users } from 'lucide-react';

export function TeamTab() {
    const players = useStore((state) => state.players);
    const selectedPlayerId = useStore((state) => state.selectedPlayerId);
    const apiStats = useStore((state) => state.apiStats);

    if (selectedPlayerId) {
        return <PlayerProfile playerId={selectedPlayerId} />;
    }

    return (
        <div className="h-full flex flex-col">
            <div className="flex items-center gap-3 mb-8">
                <div className="w-10 h-10 rounded-xl bg-charcoal-800 flex items-center justify-center border border-charcoal-700">
                    <Users className="w-5 h-5 text-brand-light" />
                </div>
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Team Roster</h2>
                    <p className="text-sm text-gray-400 font-medium">{players.length > 0 ? `${players.length} Tracked Players` : 'Populated after analysis'}</p>
                </div>
            </div>

            {apiStats && (
                <div className="mb-8">
                    <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">CV Analysis — Team Comparison</h3>
                    <div className="grid grid-cols-2 gap-6 mb-4">
                        <div className="bg-charcoal-800 border border-charcoal-700 rounded-2xl p-5">
                            <span className="block text-xs font-bold text-brand-light uppercase tracking-widest mb-4">Team 1</span>
                            <div className="grid grid-cols-3 gap-4">
                                <StatCard label="Possession" value={`${apiStats.team_1.ball_acquisition_pct}%`} highlight />
                                <StatCard label="Passes" value={apiStats.team_1.passes} />
                                <StatCard label="Intercepts" value={apiStats.team_1.interceptions} />
                            </div>
                        </div>
                        <div className="bg-charcoal-800 border border-charcoal-700 rounded-2xl p-5">
                            <span className="block text-xs font-bold text-yellow-400 uppercase tracking-widest mb-4">Team 2</span>
                            <div className="grid grid-cols-3 gap-4">
                                <StatCard label="Possession" value={`${apiStats.team_2.ball_acquisition_pct}%`} highlight />
                                <StatCard label="Passes" value={apiStats.team_2.passes} />
                                <StatCard label="Intercepts" value={apiStats.team_2.interceptions} />
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {players.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 pb-8">
                    {players.map(player => (
                        <PlayerCard key={player.id} player={player} />
                    ))}
                </div>
            ) : (
                <div className="flex-1 flex flex-col items-center justify-center py-16">
                    <div className="w-14 h-14 rounded-2xl bg-charcoal-800 border border-charcoal-700 flex items-center justify-center mb-5">
                        <Users className="w-7 h-7 text-brand-light opacity-50" />
                    </div>
                    <h3 className="text-base font-bold text-white mb-2">No Players Yet</h3>
                    <p className="text-sm text-gray-500 text-center max-w-xs leading-relaxed">
                        Player tracking data will appear here once a video is processed. The model assigns each tracked player to a team and reports their stats.
                    </p>
                </div>
            )}
        </div>
    );
}
