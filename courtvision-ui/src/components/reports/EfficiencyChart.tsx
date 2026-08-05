import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { useStore } from '../../store/useStore';

export function EfficiencyChart() {
    const players = useStore((state) => state.players);
    const playerStats = useStore((state) => state.playerStats);

    // Merge player names with their stats and take top 5 scorers
    const data = playerStats
        .map(stat => ({
            name: players.find(p => p.id === stat.playerId)?.name.split(' ')[1] || 'Unknown',
            TS: stat.TS,
            eFG: stat.eFG,
            PTS: stat.points,
        }))
        .sort((a, b) => b.PTS - a.PTS)
        .slice(0, 6);

    return (
        <ResponsiveContainer width="100%" height="100%">
            <BarChart
                data={data}
                margin={{ top: 20, right: 30, left: 0, bottom: 5 }}
            >
                <CartesianGrid strokeDasharray="3 3" stroke="#272a33" vertical={false} />
                <XAxis
                    dataKey="name"
                    stroke="#9ca3af"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                />
                <YAxis
                    stroke="#9ca3af"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                    domain={[0, 100]}
                    tickFormatter={(value) => `${value}%`}
                />
                <Tooltip
                    contentStyle={{ backgroundColor: '#1a1d24', borderColor: '#272a33', color: '#f3f4f6', borderRadius: '12px', padding: '12px' }}
                    itemStyle={{ fontWeight: 'bold' }}
                />
                <Legend wrapperStyle={{ paddingTop: '10px', fontSize: '12px', color: '#9ca3af' }} />
                <Bar dataKey="TS" name="True Shooting %" fill="#7c3aed" radius={[4, 4, 0, 0]} barSize={32} />
                <Bar dataKey="eFG" name="Effective FG %" fill="#4ade80" radius={[4, 4, 0, 0]} barSize={32} />
            </BarChart>
        </ResponsiveContainer>
    );
}
