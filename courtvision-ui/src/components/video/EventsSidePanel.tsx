import { useStore } from '../../store/useStore';
import { Activity, ArrowLeftRight, ShieldAlert } from 'lucide-react';

export function EventsSidePanel() {
    const apiStats = useStore((state) => state.apiStats);

    if (!apiStats) {
        return (
            <div className="flex flex-col gap-6 py-4">
                <p className="text-xs text-gray-500 font-medium leading-relaxed">
                    Once a video is processed, the model will populate this panel in real time with detected game events.
                </p>

                <div className="space-y-3">
                    <div className="bg-charcoal-900 border border-charcoal-700 rounded-xl p-4 opacity-40">
                        <div className="flex items-center gap-2 mb-3">
                            <Activity className="w-4 h-4 text-brand-light" />
                            <span className="text-xs font-bold text-gray-400 uppercase tracking-widest">Ball Possession</span>
                        </div>
                        <p className="text-xs text-gray-500">Which team currently has the ball, updated frame-by-frame.</p>
                    </div>

                    <div className="bg-charcoal-900 border border-charcoal-700 rounded-xl p-4 opacity-40">
                        <div className="flex items-center gap-2 mb-3">
                            <ArrowLeftRight className="w-4 h-4 text-blue-400" />
                            <span className="text-xs font-bold text-gray-400 uppercase tracking-widest">Passes</span>
                        </div>
                        <p className="text-xs text-gray-500">Pass count per team, detected when possession transfers between teammates.</p>
                    </div>

                    <div className="bg-charcoal-900 border border-charcoal-700 rounded-xl p-4 opacity-40">
                        <div className="flex items-center gap-2 mb-3">
                            <ShieldAlert className="w-4 h-4 text-yellow-400" />
                            <span className="text-xs font-bold text-gray-400 uppercase tracking-widest">Interceptions</span>
                        </div>
                        <p className="text-xs text-gray-500">Detected when possession transfers to the opposing team.</p>
                    </div>
                </div>
            </div>
        );
    }

    const possessionTeam = apiStats.team_1.ball_acquisition_pct >= apiStats.team_2.ball_acquisition_pct ? 1 : 2;

    return (
        <div className="flex flex-col gap-4 py-2">
            {/* Ball possession */}
            <div className="bg-charcoal-900 border border-brand/30 rounded-xl p-4">
                <div className="flex items-center gap-2 mb-3">
                    <Activity className="w-4 h-4 text-brand-light" />
                    <span className="text-xs font-bold text-brand-light uppercase tracking-widest">Ball Possession</span>
                </div>
                <div className="flex gap-3">
                    <div className={`flex-1 rounded-lg p-3 text-center ${possessionTeam === 1 ? 'bg-brand/20 border border-brand/40' : 'bg-charcoal-800 border border-charcoal-700'}`}>
                        <span className="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Team 1</span>
                        <span className="block text-2xl font-black text-white">{apiStats.team_1.ball_acquisition_pct}%</span>
                    </div>
                    <div className={`flex-1 rounded-lg p-3 text-center ${possessionTeam === 2 ? 'bg-yellow-400/20 border border-yellow-400/40' : 'bg-charcoal-800 border border-charcoal-700'}`}>
                        <span className="block text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Team 2</span>
                        <span className="block text-2xl font-black text-white">{apiStats.team_2.ball_acquisition_pct}%</span>
                    </div>
                </div>
            </div>

            {/* Passes */}
            <div className="bg-charcoal-900 border border-charcoal-700 rounded-xl p-4">
                <div className="flex items-center gap-2 mb-3">
                    <ArrowLeftRight className="w-4 h-4 text-blue-400" />
                    <span className="text-xs font-bold text-gray-400 uppercase tracking-widest">Passes</span>
                </div>
                <div className="flex gap-3">
                    <div className="flex-1 bg-charcoal-800 border border-charcoal-700 rounded-lg p-3 text-center">
                        <span className="block text-[10px] font-bold text-brand-light uppercase tracking-widest mb-1">Team 1</span>
                        <span className="block text-2xl font-black text-white">{apiStats.team_1.passes}</span>
                    </div>
                    <div className="flex-1 bg-charcoal-800 border border-charcoal-700 rounded-lg p-3 text-center">
                        <span className="block text-[10px] font-bold text-yellow-400 uppercase tracking-widest mb-1">Team 2</span>
                        <span className="block text-2xl font-black text-white">{apiStats.team_2.passes}</span>
                    </div>
                </div>
            </div>

            {/* Interceptions */}
            <div className="bg-charcoal-900 border border-charcoal-700 rounded-xl p-4">
                <div className="flex items-center gap-2 mb-3">
                    <ShieldAlert className="w-4 h-4 text-yellow-400" />
                    <span className="text-xs font-bold text-gray-400 uppercase tracking-widest">Interceptions</span>
                </div>
                <div className="flex gap-3">
                    <div className="flex-1 bg-charcoal-800 border border-charcoal-700 rounded-lg p-3 text-center">
                        <span className="block text-[10px] font-bold text-brand-light uppercase tracking-widest mb-1">Team 1</span>
                        <span className="block text-2xl font-black text-white">{apiStats.team_1.interceptions}</span>
                    </div>
                    <div className="flex-1 bg-charcoal-800 border border-charcoal-700 rounded-lg p-3 text-center">
                        <span className="block text-[10px] font-bold text-yellow-400 uppercase tracking-widest mb-1">Team 2</span>
                        <span className="block text-2xl font-black text-white">{apiStats.team_2.interceptions}</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
