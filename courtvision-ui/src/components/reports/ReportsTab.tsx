import { BarChart2, Activity, ArrowLeftRight, ShieldAlert, Cpu } from 'lucide-react';
import { useStore } from '../../store/useStore';

export function ReportsTab() {
    const apiStats = useStore((state) => state.apiStats);

    return (
        <div className="h-full flex flex-col pb-8">
            <div className="flex items-center gap-3 mb-8">
                <div className="w-10 h-10 rounded-xl bg-charcoal-800 flex items-center justify-center border border-charcoal-700">
                    <BarChart2 className="w-5 h-5 text-brand" />
                </div>
                <div>
                    <h2 className="text-2xl font-bold tracking-tight text-white">Team Analytics</h2>
                    <p className="text-sm text-gray-400 font-medium">CV Pipeline Output</p>
                </div>
            </div>

            {apiStats ? (
                <div className="space-y-6">
                    {/* Ball Possession */}
                    <div className="bg-charcoal-800 border border-charcoal-700 rounded-2xl p-6">
                        <div className="flex items-center gap-2 mb-5">
                            <Activity className="w-4 h-4 text-brand-light" />
                            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider">Ball Possession</h3>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="bg-charcoal-900 border border-brand/30 rounded-xl p-5 text-center">
                                <span className="block text-[10px] font-bold text-brand-light uppercase tracking-widest mb-2">Team 1</span>
                                <span className="block text-4xl font-black text-white">{apiStats.team_1.ball_acquisition_pct}%</span>
                            </div>
                            <div className="bg-charcoal-900 border border-yellow-400/30 rounded-xl p-5 text-center">
                                <span className="block text-[10px] font-bold text-yellow-400 uppercase tracking-widest mb-2">Team 2</span>
                                <span className="block text-4xl font-black text-white">{apiStats.team_2.ball_acquisition_pct}%</span>
                            </div>
                        </div>
                    </div>

                    {/* Passes */}
                    <div className="bg-charcoal-800 border border-charcoal-700 rounded-2xl p-6">
                        <div className="flex items-center gap-2 mb-5">
                            <ArrowLeftRight className="w-4 h-4 text-blue-400" />
                            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider">Passes</h3>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="bg-charcoal-900 border border-charcoal-700 rounded-xl p-5 text-center">
                                <span className="block text-[10px] font-bold text-brand-light uppercase tracking-widest mb-2">Team 1</span>
                                <span className="block text-4xl font-black text-white">{apiStats.team_1.passes}</span>
                            </div>
                            <div className="bg-charcoal-900 border border-charcoal-700 rounded-xl p-5 text-center">
                                <span className="block text-[10px] font-bold text-yellow-400 uppercase tracking-widest mb-2">Team 2</span>
                                <span className="block text-4xl font-black text-white">{apiStats.team_2.passes}</span>
                            </div>
                        </div>
                    </div>

                    {/* Interceptions */}
                    <div className="bg-charcoal-800 border border-charcoal-700 rounded-2xl p-6">
                        <div className="flex items-center gap-2 mb-5">
                            <ShieldAlert className="w-4 h-4 text-yellow-400" />
                            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider">Interceptions</h3>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="bg-charcoal-900 border border-charcoal-700 rounded-xl p-5 text-center">
                                <span className="block text-[10px] font-bold text-brand-light uppercase tracking-widest mb-2">Team 1</span>
                                <span className="block text-4xl font-black text-white">{apiStats.team_1.interceptions}</span>
                            </div>
                            <div className="bg-charcoal-900 border border-charcoal-700 rounded-xl p-5 text-center">
                                <span className="block text-[10px] font-bold text-yellow-400 uppercase tracking-widest mb-2">Team 2</span>
                                <span className="block text-4xl font-black text-white">{apiStats.team_2.interceptions}</span>
                            </div>
                        </div>
                    </div>
                </div>
            ) : (
                <div className="flex-1 flex flex-col items-center justify-center">
                    <div className="w-16 h-16 rounded-2xl bg-charcoal-800 border border-charcoal-700 flex items-center justify-center mb-6">
                        <Cpu className="w-8 h-8 text-brand-light opacity-60" />
                    </div>
                    <h3 className="text-lg font-bold text-white mb-2">Waiting for Analysis</h3>
                    <p className="text-sm text-gray-500 text-center max-w-sm leading-relaxed">
                        Upload and process a game video. The CV pipeline will automatically extract and display real-time stats here.
                    </p>

                    <div className="mt-10 grid grid-cols-1 gap-3 w-full max-w-sm">
                        <div className="bg-charcoal-800 border border-charcoal-700 rounded-xl p-4 flex items-center gap-4 opacity-50">
                            <Activity className="w-5 h-5 text-brand-light flex-shrink-0" />
                            <div>
                                <span className="block text-xs font-bold text-white">Ball Possession %</span>
                                <span className="block text-xs text-gray-500 mt-0.5">Which team controls the ball over time</span>
                            </div>
                        </div>
                        <div className="bg-charcoal-800 border border-charcoal-700 rounded-xl p-4 flex items-center gap-4 opacity-50">
                            <ArrowLeftRight className="w-5 h-5 text-blue-400 flex-shrink-0" />
                            <div>
                                <span className="block text-xs font-bold text-white">Pass Count per Team</span>
                                <span className="block text-xs text-gray-500 mt-0.5">Detected when possession transfers between teammates</span>
                            </div>
                        </div>
                        <div className="bg-charcoal-800 border border-charcoal-700 rounded-xl p-4 flex items-center gap-4 opacity-50">
                            <ShieldAlert className="w-5 h-5 text-yellow-400 flex-shrink-0" />
                            <div>
                                <span className="block text-xs font-bold text-white">Interceptions per Team</span>
                                <span className="block text-xs text-gray-500 mt-0.5">Detected when the opposing team gains possession</span>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
