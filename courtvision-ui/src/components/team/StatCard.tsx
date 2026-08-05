export function StatCard({ label, value, highlight = false }: { label: string, value: string | number, highlight?: boolean }) {
    return (
        <div className={`p-5 rounded-2xl border ${highlight ? 'bg-brand/10 border-brand/30' : 'bg-charcoal-900/50 border-charcoal-700'}`}>
            <span className="block text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">{label}</span>
            <span className={`block text-2xl font-black leading-none ${highlight ? 'text-brand-light' : 'text-white'}`}>
                {value}
            </span>
        </div>
    );
}
