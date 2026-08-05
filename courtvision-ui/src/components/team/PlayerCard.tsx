import { useStore } from '../../store/useStore';
import { Player } from '../../data/mock';
import { ChevronRight } from 'lucide-react';

export function PlayerCard({ player }: { player: Player }) {
    const setSelectedPlayerId = useStore((state) => state.setSelectedPlayerId);
    const stats = useStore((state) => state.playerStats.find(s => s.playerId === player.id));

    return (
        <button
            onClick={() => setSelectedPlayerId(player.id)}
            className="group relative bg-charcoal-800 border border-charcoal-700 rounded-2xl p-6 text-left transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-brand/5 hover:border-brand-light/50 overflow-hidden"
        >
            <div className="absolute -right-4 -top-4 text-[100px] font-black italic text-charcoal-700/30 group-hover:text-charcoal-700/50 transition-colors pointer-events-none leading-none z-0">
                {player.jersey}
            </div>

            <div className="relative z-10">
                <div className="flex justify-between items-start mb-6">
                    <div>
                        <span className="inline-block px-2 py-1 rounded bg-charcoal-900 border border-charcoal-700 text-brand-light text-xs font-bold tracking-widest mb-3">
                            {player.position}
                        </span>
                        <h3 className="text-xl font-bold text-white tracking-tight">{player.name}</h3>
                    </div>
                </div>

                <div className="grid grid-cols-3 gap-4 border-t border-charcoal-700 pt-5 mt-auto">
                    <div>
                        <span className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">PTS</span>
                        <span className="block text-xl font-bold text-white leading-none">{stats?.points || '-'}</span>
                    </div>
                    <div>
                        <span className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">eFG%</span>
                        <span className="block text-xl font-bold text-white leading-none">{stats?.eFG || '-'}</span>
                    </div>
                    <div>
                        <span className="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">TS%</span>
                        <span className="block text-xl font-bold text-white leading-none">{stats?.TS || '-'}</span>
                    </div>
                </div>

                <div className="absolute bottom-6 right-6 opacity-0 group-hover:opacity-100 transform translate-x-2 group-hover:translate-x-0 transition-all duration-300">
                    <div className="w-8 h-8 rounded-full bg-brand flex items-center justify-center text-white">
                        <ChevronRight className="w-5 h-5" />
                    </div>
                </div>
            </div>
        </button>
    );
}
