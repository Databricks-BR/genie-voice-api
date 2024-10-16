import React, { useState } from 'react';
import { Card, CardContent, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, MenuItem, Select } from '@mui/material';
import { styled } from '@mui/system';

const TotalRow = styled(TableRow)(({ theme }) => ({
  backgroundColor: theme.palette.grey[200],
  fontWeight: 'bold',
}));

function ProfitLoss({ selectedAccount, accountData }) {
  const { profitLoss } = accountData[selectedAccount];
  const [selectedMetric, setSelectedMetric] = useState('monthly');

  const handleMetricChange = (event) => {
    setSelectedMetric(event.target.value);
  };

  const metrics = ['daily', 'weekly', 'monthly', 'yearly'];
  const metricLabels = {
    daily: 'Daily',
    weekly: 'Weekly',
    monthly: 'Monthly',
    yearly: 'Yearly'
  };

  const additionalMetrics = {
    daily: { avg: 50, high: 100, low: -50, trades: 10 },
    weekly: { avg: 300, high: 700, low: -200, trades: 50},
    monthly: { avg: 1000, high: 3000, low: -1000, trades: 200 },
    yearly: { avg: 12000, high: 30000, low: -5000, trades: 300 }
  };

  return (
    <Card sx={{height: 482}}>
      <CardContent>
        <Typography variant="h6">Inputs/Outputs</Typography>
        <Select
          value={selectedMetric}
          onChange={handleMetricChange}
          fullWidth
          variant="outlined"
          style={{ marginBottom: '10px' }}
        >
          {metrics.map(metric => (
            <MenuItem value={metric} key={metric}>{metricLabels[metric]}</MenuItem>
          ))}
        </Select>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Metric</TableCell>
                <TableCell align="right">Amount</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              <TableRow>
                <TableCell component="th" scope="row">
                  Amount
                </TableCell>
                <TableCell align="right" style={{ color: profitLoss[selectedMetric].amount >= 0 ? 'green' : 'red' }}>
                  {profitLoss[selectedMetric].amount >= 0 ? `+$${profitLoss[selectedMetric].amount}` : `-$${Math.abs(profitLoss[selectedMetric].amount)}`}
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell component="th" scope="row">
                Percentage
                </TableCell>
                <TableCell align="right" style={{ color: profitLoss[selectedMetric].percentage >= 0 ? 'green' : 'red' }}>
                  {profitLoss[selectedMetric].percentage >= 0 ? `+${profitLoss[selectedMetric].percentage}%` : `${profitLoss[selectedMetric].percentage}%`}
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell component="th" scope="row">
                Total Operations
                </TableCell>
                <TableCell align="right">
                  {additionalMetrics[selectedMetric].trades}
                </TableCell>
              </TableRow>
              <TotalRow>
                <TableCell component="th" scope="row">
                  Inputs/Outputs (Value)
                </TableCell>
                <TableCell align="right" style={{ color: profitLoss['total'].amount >= 0 ? 'green' : 'red' }}>
                  {profitLoss['total'].amount >= 0 ? `+$${profitLoss['total'].amount}` : `-$${Math.abs(profitLoss['total'].amount)}`}
                </TableCell>
              </TotalRow>
              <TotalRow>
                <TableCell component="th" scope="row">
                Inputs/Outputs (%)
                </TableCell>
                <TableCell align="right" style={{ color: profitLoss['total'].amount >= 0 ? 'green' : 'red' }}>
                  {profitLoss['total'].amount >= 0 ? `+${profitLoss['total'].percentage}%` : `-${Math.abs(profitLoss['total'].percentage)}%`}
                </TableCell>
              </TotalRow>              
            </TableBody>
          </Table>
      </CardContent>
    </Card>
  );
}

export default ProfitLoss;