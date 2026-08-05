import { Download } from 'lucide-react';

export function Topbar() {
    return (
        <header className="h-20 bg-charcoal-900 border-b border-charcoal-800 flex items-center justify-between px-8 shrink-0">
            <div>
                <h1 className="text-xl font-bold text-white tracking-tight">Lakers vs Warriors</h1>
                <p className="text-sm text-gray-400 font-medium mt-0.5">Game 4 • Western Conference Semifinals</p>
            </div>

            <div className="flex items-center gap-6">
                <div className="flex items-center gap-4 pr-6 border-r border-charcoal-700">
                    <div className="text-right">
                        <span className="text-xs font-bold text-gray-400 uppercase tracking-widest block mb-0.5">LAL</span>
                        <span className="text-2xl font-black text-white leading-none">105</span>
                    </div>
                    <div className="w-px h-8 bg-charcoal-700 hidden sm:block"></div>
                    <div className="text-left">
                        <span className="text-xs font-bold text-gray-400 uppercase tracking-widest block mb-0.5">GSW</span>
                        <span className="text-2xl font-black text-gray-300 leading-none">108</span>
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
