import { Video, Users, BarChart2, CheckCircle2 } from 'lucide-react';
import { useStore, TabType } from '../../store/useStore';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function Sidebar() {
    const currentTab = useStore(state => state.currentTab);
    const setCurrentTab = useStore(state => state.setCurrentTab);

    const tabs: { id: TabType; label: string; icon: React.ReactNode }[] = [
        { id: 'video', label: 'Video', icon: <Video className="w-5 h-5" /> },
        { id: 'team', label: 'Team', icon: <Users className="w-5 h-5" /> },
        { id: 'reports', label: 'Reports', icon: <BarChart2 className="w-5 h-5" /> },
    ];

    return (
        <aside className="w-64 bg-charcoal-950 border-r border-charcoal-800 h-full flex flex-col pt-6">
            <div className="px-6 mb-8 flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-brand flex items-center justify-center">
                    <Video className="w-5 h-5 text-white" />
                </div>
                <span className="font-bold text-xl tracking-tight">CourtVision</span>
            </div>

            <nav className="flex-1 px-4 space-y-2">
                {tabs.map(tab => {
                    const isActive = currentTab === tab.id;
                    return (
                        <button
                            key={tab.id}
                            onClick={() => setCurrentTab(tab.id)}
                            className={twMerge(
                                clsx(
                                    "w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all duration-200",
                                    isActive
                                        ? "bg-brand/10 text-brand-light"
                                        : "text-gray-400 hover:text-gray-200 hover:bg-charcoal-800"
                                )
                            )}
                        >
                            <div className={clsx(isActive ? "text-brand" : "text-gray-500")}>
                                {tab.icon}
                            </div>
                            {tab.label}
                            {isActive && (
                                <div className="ml-auto w-1 h-1 rounded-full bg-brand-light shadow-[0_0_8px_var(--color-brand)]" />
                            )}
                        </button>
                    );
                })}
            </nav>

            <div className="p-6 border-t border-charcoal-800">
                <div className="flex items-center gap-3 mb-2">
                    <CheckCircle2 className="w-4 h-4 text-green-400" />
                    <span className="text-sm font-medium text-gray-300">Processing Complete</span>
                </div>
                <div className="text-xs text-brand-light flex justify-between">
                    <span>Final Game Data</span>
                    <span>100%</span>
                </div>
                <div className="w-full h-1.5 bg-charcoal-800 rounded-full mt-2 overflow-hidden">
                    <div className="h-full bg-brand w-full" />
                </div>
            </div>
        </aside>
    );
}
