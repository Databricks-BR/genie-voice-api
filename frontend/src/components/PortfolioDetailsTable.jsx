import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Button } from '@mui/material';
import { styled } from '@mui/system';

const StyledTableCell = styled(TableCell)(({ theme }) => ({
  fontWeight: 'bold',
  backgroundColor: theme.palette.grey[200],
}));

const PerformanceCell = styled(TableCell)(({ value }) => ({
  color: value.startsWith('+') ? 'green' : 'red',
  fontWeight: 'bold',
}));

const stockData = {
  'Cartão': { name: 'Apple', ticker: 'AAPL', industry: 'Cartão', last15d: '+5%', lastMonth: '+10%' },
  'Alimentação': { name: 'JPMorgan', ticker: 'JPM', industry: 'Alimentação', last15d: '+3%', lastMonth: '+6%' },
  'Saúde': { name: 'Pfizer', ticker: 'PFE', industry: 'Healthcare', last15d: '+2%', lastMonth: '+5%' },
  'Combustível': { name: 'ExxonMobil', ticker: 'XOM', industry: 'Combustível', last15d: '+1%', lastMonth: '+4%' },
};

function PortfolioDetailsTable({ selectedAccount, accountData }) {
  const navigate = useNavigate();
  const industries = accountData[selectedAccount].industry;
  const stocks = industries.map(industry => {
    const stock = stockData[industry.name];
    const value = industry.value;
    const sharePrice = Math.round((value / 1000) * 100) / 100; // Simplified share price for example
    const shareNum = Math.round(value / sharePrice);
    return { ...stock, marketCap: `${(value / 1000).toFixed(1)}B`, shareNum, sharePrice, value };
  });

  return (
    <Card style={{ marginTop: '20px' }}>
      <CardContent>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <StyledTableCell>Company Name</StyledTableCell>
                <StyledTableCell>Ticker</StyledTableCell>
                <StyledTableCell>Industry</StyledTableCell>
                <StyledTableCell>Market Cap</StyledTableCell>
                <StyledTableCell>Share Number</StyledTableCell>
                <StyledTableCell>Share Price</StyledTableCell>
                <StyledTableCell>Value</StyledTableCell>
                <StyledTableCell>Last 15d</StyledTableCell>
                <StyledTableCell>Last Month</StyledTableCell>
                <StyledTableCell></StyledTableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {stocks.map((row) => (
                <TableRow key={row.ticker}>
                  <TableCell>{row.name}</TableCell>
                  <TableCell>{row.ticker}</TableCell>
                  <TableCell>{row.industry}</TableCell>
                  <TableCell>{row.marketCap}</TableCell>
                  <TableCell>{row.shareNum}</TableCell>
                  <TableCell>${row.sharePrice}</TableCell>
                  <TableCell>${row.value}</TableCell>
                  <PerformanceCell value={row.last15d}>{row.last15d}</PerformanceCell>
                  <PerformanceCell value={row.lastMonth}>{row.lastMonth}</PerformanceCell>
                  <TableCell>
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={() => {
                        window.scrollTo(0, 0); // Scroll to the top
                        navigate(`/details/${row.ticker}`);
                      }}
                      disabled={row.ticker !== 'AAPL'}
                      sx={{
                        color: row.ticker !== 'AAPL' ? 'grey' : 'primary.main',
                        borderColor: row.ticker !== 'AAPL' ? 'grey' : 'primary.main',
                      }}
                    >
                      See details
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </CardContent>
    </Card>
  );
}

export default PortfolioDetailsTable;