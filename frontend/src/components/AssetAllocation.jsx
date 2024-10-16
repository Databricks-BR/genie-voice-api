import React from 'react';
import { Card, CardContent, Typography } from '@mui/material';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const COLORS = ['#98102A', '#1B3139', '#00A972', '#2272B4'];

function AssetAllocation({ selectedAccount, accountData }) {
  const data = accountData[selectedAccount].assetClass;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6">Overall Asset Allocation</Typography>
        <ResponsiveContainer width="100%" height={388}>
          <PieChart width={400} height={300}>
            <Pie
              data={data}
              cx="50%"
              cy="45%"
              labelLine={false}
              outerRadius={150}
              fill="#8884d8"
              dataKey="value"
              nameKey="name"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

export default AssetAllocation;