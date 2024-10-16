import React from 'react';
import { Grid, Card, CardContent, Typography } from '@mui/material';
import { PieChart, Pie, Cell, Tooltip, Legend, LineChart, Line, XAxis, YAxis, CartesianGrid, Area, ResponsiveContainer } from 'recharts';

const calculateMovingAverage = (data, windowSize) => {
  return data.map((val, idx, arr) => {
    if (idx < windowSize - 1) return { ...val, avg: null }; // Not enough data to calculate average
    const window = arr.slice(idx - windowSize + 1, idx + 1);
    const sum = window.reduce((acc, curr) => acc + curr.value, 0);
    return { ...val, avg: sum / windowSize };
  });
};

const COLORS = ['#FF5F46', '#4299E0', '#42BA91', '#BD802B'];

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

function PortfolioCharts({ selectedAccount, accountData }) {
  const data = accountData[selectedAccount].ytd;
  const dataWithMovingAverage = calculateMovingAverage(data, 3); // 3-month moving average

  return (
    <Grid container spacing={3} sx={{ marginTop: 1 }}>
      <Grid item xs={12} sm={6}>
        <Card>
          <CardContent>
            <Typography variant="h6">Tipo de Gastos</Typography>
            <ResponsiveContainer width="100%" height={400}>
              <PieChart>
                <Pie
                  data={accountData[selectedAccount].industry}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={150}
                  fill="#8884d8"
                  dataKey="value"
                  nameKey="name"
                >
                  {accountData[selectedAccount].industry.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} sm={6}>
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
      </Grid>
    </Grid>
  );
}

export default PortfolioCharts;