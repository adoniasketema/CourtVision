import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export function SituationalChart() {
    // Mock data for situational points
    const data = [
        { name: 'Points in Paint', value: 48, fill: '#7c3aed' },
        { name: 'Fast Break Points', value: 18, fill: '#8b5cf6' },
        { name: 'Second Chance', value: 14, fill: '#a78bfa' },
        { name: 'Points off TOV', value: 21, fill: '#c4b5fd' },
        { name: 'Bench Points', value: 32, fill: '#ddd6fe' },
    ];

    return (
        <ResponsiveContainer width="100%" height="100%">
            <BarChart
                data={data}
                layout="vertical"
                margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
            >
                <CartesianGrid strokeDasharray="3 3" stroke="#272a33" horizontal={true} vertical={false} />
                <XAxis type="number" stroke="#9ca3af" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis
                    dataKey="name"
                    type="category"
                    stroke="#9ca3af"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                    width={110}
                />
                <Tooltip
                    cursor={{ fill: '#272a33', opacity: 0.4 }}
                    contentStyle={{ backgroundColor: '#1a1d24', borderColor: '#272a33', color: '#f3f4f6', borderRadius: '12px', padding: '12px' }}
                    itemStyle={{ fontWeight: 'bold' }}
                />
                <Bar dataKey="value" name="Points" radius={[0, 4, 4, 0]} barSize={24} />
            </BarChart>
        </ResponsiveContainer>
    );
}
