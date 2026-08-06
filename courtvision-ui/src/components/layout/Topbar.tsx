import { Download } from 'lucide-react';
import { useStore } from '../../store/useStore';

export function Topbar() {
    const apiStats = useStore((state) => state.apiStats);
    
    // @ts-ignore
    const scoreboard = apiStats?.scoreboard || null;
    const team1Name = scoreboard?.team_1_name || 'Lakers';
    const team2Name = scoreboard?.team_2_name || 'Warriors';
    const score1 = scoreboard?.score_1 ?? 105;
    const score2 = scoreboard?.score_2 ?? 108;
    const subtitle = scoreboard ? 'CV Auto-Detected Matchup' : 'Game 4 • Western Conference Semifinals';

    return (
        <header className="h-20 bg-charcoal-900 border-b border-charcoal-800 flex items-center justify-between px-8 shrink-0">
            <div>
                <h1 className="text-xl font-bold text-white tracking-tight">{team1Name} vs {team2Name}</h1>
                <p className="text-sm text-gray-400 font-medium mt-0.5">{subtitle}</p>
            </div>

            <div className="flex items-center gap-6">
                <div className="flex items-center gap-4 pr-6 border-r border-charcoal-700">
                    <div className="text-right">
                        <span className="text-xs font-bold text-brand-light uppercase tracking-widest block mb-0.5">T1</span>
                        <span className="text-2xl font-black text-white leading-none">{score1}</span>
                    </div>
                    <div className="w-px h-8 bg-charcoal-700 hidden sm:block"></div>
                    <div className="text-left">
                        <span className="text-xs font-bold text-yellow-400 uppercase tracking-widest block mb-0.5">T2</span>
                        <span className="text-2xl font-black text-gray-300 leading-none">{score2}</span>
                    </div>
                </div>

                <button className="flex items-center gap-2 bg-charcoal-800 hover:bg-charcoal-700 px-4 py-2.5 rounded-lg text-sm font-semibold transition-colors text-white">
                    <Download className="w-4 h-4 text-gray-400" />
                    Export Data
                </button>
            </div>
        </header>
    );
}
