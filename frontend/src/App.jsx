import React, { useState } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import {
  Container,
  CssBaseline,
  ThemeProvider,
  createTheme,
  Grid,
} from "@mui/material";
import Header from "./components/Header";
import PortfolioSummary from "./components/PortfolioSummary";
import ProfitLoss from "./components/ProfitLoss";
import AssetAllocation from "./components/AssetAllocation";
import PortfolioCharts from "./components/PortfolioCharts";
import PortfolioDetailsTable from "./components/PortfolioDetailsTable";
import PortfolioDashboard from "./components/PortfolioDashboard";
import DetailView from "./pages/DetailView";
import ReportDetail from "./pages/ReportDetail";
import Chatbot from "./components/Chatbot";
import PortfolioLineChart from "./components/PortfolioLineChart";
import IndustryPieChart from "./components/IndustryPieChart";
import { ChatbotProvider } from "./components/ChatbotContext";

//  To-do:
//  -- rethink pie chart coloring, get feedback there.

// Theme Configuration
const theme = createTheme({
  palette: {
    primary: {
      main: "#FF3621", // Orange 600
    },
    secondary: {
      main: "#1B3139", // Navy 800
    },
    background: {
      default: "#F9F7F4", // Oat Light
    },
    text: {
      primary: "#1B3139", // Navy 800
      secondary: "#555",
    },
  },
  typography: {
    fontFamily: '"DM Sans", Arial, sans-serif',
    h4: {
      fontWeight: 700,
      marginBottom: "20px",
    },
    h6: {
      fontWeight: 500,
      marginBottom: "10px",
    },
    body1: {
      fontSize: "1rem",
      marginBottom: "10px",
    },
    button: {
      textTransform: "none",
    },
  },
  shape: {
    borderRadius: 8,
  },
  spacing: 8,
});

const accountData = {
  "Sicoob": {
    value: 392807,
    profitLoss: {
      daily: { amount: 423, percentage: 0.12 },
      weekly: { amount: -4.259, percentage: -0.5 },
      monthly: { amount: -58.934, percentage: -12.0 },
      yearly: { amount: -70.208, percentage: -8.0 },
      total: { amount: -15.231, percentage: -12.17 },
    },
    industry: [
      { name: "Restaurants", value: 413.479 },
      { name: "Withdrawals", value: 399.523 },
      { name: "Housing", value: 393.135 },
      { name: "Pets", value: 376.056 },
    ],
    ytd: [
      { month: "Jan", value: 10965 },
      { month: "Feb", value: 4300 },
      { month: "Mar", value: 12580 },
      { month: "Apr", value: 500 },
      { month: "May", value: 58000 },
      { month: "Jun", value: 18360 },
      { month: "Jul", value: 5963 },
    ]
  },
  "Itaú Unibanco": {
    value: 43862,
    profitLoss: {
      daily: { amount: 456, percentage: 0.12 },
      weekly: { amount: 250, percentage: 0.5 },
      monthly: { amount: 100, percentage: 2.0 },
      yearly: { amount: 2000, percentage: 4.0 },
      total: { amount: 5231, percentage: 5.23 },
    },
    industry: [
      { name: "Credit Card", value: 12589 },
      { name: "Food", value: 1800 },
      { name: "Health", value: 20000 },
      { name: "Gas", value: 15231 },
    ],
    ytd: [
      { month: "Jan", value: 10965 },
      { month: "Feb", value: 4300 },
      { month: "Mar", value: 12580 },
      { month: "Apr", value: 500 },
      { month: "May", value: 58000 },
      { month: "Jun", value: 18360 },
      { month: "Jul", value: 5963 },
    ]
  },
  "Caixa Econômica Federal": {
    value: 941,
    profitLoss: {
      daily: { amount: 12.98, percentage: 0.12 },
      weekly: { amount: 98.99, percentage: 0.5 },
      monthly: { amount: 2850, percentage: 2.0 },
      yearly: { amount: 25690, percentage: 4.0 },
      total: { amount: 5231, percentage: 5.23 },
    },
    industry: [
      { name: "Credit Card", value: 40000 },
      { name: "Food", value: 30000 },
      { name: "Gas", value: 20000 },
      { name: "Health", value: 15231 },
    ],
    ytd: [
      { month: "Jan", value: 10965 },
      { month: "Feb", value: 4300 },
      { month: "Mar", value: 12580 },
      { month: "Apr", value: 500 },
      { month: "May", value: 58000 },
      { month: "Jun", value: 18360 },
      { month: "Jul", value: 5963 },
    ]
  },
};

function App() {
  const [selectedAccount, setSelectedAccount] = useState("Sicoob");

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <ChatbotProvider>
        <Router>
          <Header />
          <Container style={{ marginTop: "100px" }}>
            <Routes>
              <Route
                path="/"
                element={
                  <>
                    <PortfolioSummary
                      selectedAccount={selectedAccount}
                      setSelectedAccount={setSelectedAccount}
                      accountData={accountData}
                    />
                    <Grid container spacing={3} style={{ marginTop: "20px" }}>
                      <Grid item xs={12} sm={6}>
                        <ProfitLoss
                          selectedAccount={selectedAccount}
                          accountData={accountData}
                        />
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <IndustryPieChart
                          industryData={accountData[selectedAccount].industry}
                        />
                      </Grid>
                      <Grid item xs={12} sm={12}>
                      {/*<PortfolioLineChart
                          ytdData={accountData[selectedAccount].ytd}
                        />*/}
                      </Grid>
                    </Grid>
                    {/*<PortfolioDetailsTable
                      selectedAccount={selectedAccount}
                      accountData={accountData}
                    />*/}
                    <PortfolioDashboard
                    />
                  </>
                }
              />
              <Route path="/details/:ticker" element={<DetailView />} />
              <Route path="/reports/:reportName" element={<ReportDetail />} />
            </Routes>
          </Container>
          <Chatbot />
        </Router>
      </ChatbotProvider>
    </ThemeProvider>
  );
}

export default App;
