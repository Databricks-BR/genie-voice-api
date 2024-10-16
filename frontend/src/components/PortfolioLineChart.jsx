import React from 'react';
import { Card, CardContent, Typography } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, Area, ResponsiveContainer } from 'recharts';

const calculateMovingAverage = (data, windowSize) => {
  return data.map((val, idx, arr) => {
    if (idx < windowSize - 1) return { ...val, avg: null }; // Not enough data to calculate average
    const window = arr.slice(idx - windowSize + 1, idx + 1);
    const sum = window.reduce((acc, curr) => acc + curr.value, 0);
    return { ...val, avg: sum / windowSize };
  });
};

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="custom-tooltip" style={{ backgroundColor: '#ffffff', padding: '10px', border: '1px solid #cccccc' }}>
        <p className="label" style={{ fontWeight: 'bold', color: '#666666' }}>{`${label} : ${payload[0].value}`}</p>
      </div>
    );
  }
  return null;
};

function PortfolioLineChart({ ytdData }) {
  const dataWithMovingAverage = calculateMovingAverage(ytdData, 3); // 3-month moving average

  return (
    <Card>
      <CardContent>
        <Typography variant="h6">Follow-up</Typography>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart
            data={dataWithMovingAverage}
            margin={{
              top: 20, right: 30, left: 20, bottom: 5,
            }}
          >
            <defs>
              <linearGradient id="colorUv" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#FF3621" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#FF3621" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis dataKey="month" tick={{ fill: 'black', fontWeight: 'bold' }} />
            <YAxis tick={{ fill: 'black', fontWeight: 'bold' }} />
            <Tooltip content={<CustomTooltip />} />
            <Legend verticalAlign="top" height={36} />
            <Area type="monotone" dataKey="value" stroke="#FF3621" fillOpacity={1} fill="url(#colorUv)" />
            <Line type="monotone" dataKey="value" stroke="black" strokeWidth={3} dot={{ r: 6, stroke: '#FF3621', strokeWidth: 2 }} activeDot={{ r: 8 }} />
            <Line type="monotone" dataKey="avg" stroke="#00BFA6" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

export default PortfolioLineChart;