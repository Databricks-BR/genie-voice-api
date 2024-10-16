import React, { useState } from 'react';
import {
  Avatar,
  Container,
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  MobileStepper,
  TextField
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import KeyboardArrowLeft from '@mui/icons-material/KeyboardArrowLeft';
import KeyboardArrowRight from '@mui/icons-material/KeyboardArrowRight';
import { useNavigate } from 'react-router-dom';
import { RadialBarChart, RadialBar, PolarAngleAxis, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import twitterIcon from '../assets/twitter.png';
import bloombergIcon from '../assets/bloomberg.jpg';
import databricksLogo from '../assets/databricks_small.png';
import ReactMarkdown from 'react-markdown';
import { useChatbot } from '../components/ChatbotContext';
import appleLogo from '../assets/apple.png'; // Adjust the path to where your logo is stored


import { useParams } from 'react-router-dom';

const reports = [
  { name: 'Earnings Report Q3 2023', type: 'Earnings Call', sentiment: 'Positive | 78%' },
  { name: 'Earnings Report Q2 2023', type: 'Earnings Call', sentiment: 'Positive | 90%' },
  { name: 'Earnings Report Q1 2023', type: 'Earnings Call', sentiment: 'Mixed | 59%' },
];

const newsItems = [
  { title: 'Reddit', description: 'Appears in r/wallstreetbets', icon: 'https://www.redditstatic.com/desktop2x/img/favicon/apple-icon-57x57.png' },
  { title: 'Bloomberg', description: 'bloomberg.com', icon: bloombergIcon },
  { title: 'Twitter', description: 'Appears in Trending Topics', icon: twitterIcon },
  { title: 'CNBC', description: 'Latest stock market news', icon: 'https://www.cnbc.com/favicon.ico' },
  { title: 'Yahoo Finance', description: 'Market insights and updates', icon: 'https://s.yimg.com/rz/l/favicon.ico' },
  { title: 'MarketWatch', description: 'Stock market and financial news', icon: 'https://www.marketwatch.com/favicon.ico' },
];


function DetailView() {
  const navigate = useNavigate();
  const theme = useTheme();
  const [activeStep, setActiveStep] = useState(0);
  const [summaryGenerated, setSummaryGenerated] = useState(false);
  const [summaryText, setSummaryText] = useState('As of 2024, AAPL continues to demonstrate strong performance, with impressive growth in both product sales and its expanding services sector. The company’s foray into advanced Cartãonologies, including augmented reality and AI, has significantly boosted investor confidence and stock value. Given your considerable gains, it may be advantageous to consider increasing your AAPL holdings while also reviewing your portfolio for potential diversification to manage risk effectively.');
  const maxSteps = Math.ceil(newsItems.length / 3);

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const getVisibleNews = () => {
    const start = activeStep * 3;
    return newsItems.slice(start, start + 3);
  };
  const handleSummarizeClick = () => {
    openChatbotWithMessage("What does sentiment look like on Reddit for AAPL?", "Reddit + Client portfolio", "Consider");
  };

  const { reportName } = useParams();
  const { openChatbotWithMessage } = useChatbot();

  const generateSummary = () => {
    setSummaryGenerated(true);
    setSummaryText('As of 2024, AAPL continues to demonstrate strong performance, with impressive growth in both product sales and its expanding services sector. The company’s foray into advanced Cartãonologies, including augmented reality and AI, has significantly boosted investor confidence and stock value. Given your considerable gains, it may be advantageous to consider increasing your AAPL holdings while also reviewing your portfolio for potential diversification to manage risk effectively.');
  };

  const regenerateSummary = () => {
    setSummaryText('Loading...'); // Show loading sign
    setTimeout(() => {
      setSummaryText('In 2024, AAPL has maintained its upward momentum, fueled by strong product sales and rapid growth in its services business. The company’s innovation in areas like augmented reality and artificial intelligence has further solidified investor confidence, driving stock prices higher. Given your substantial returns, it would be wise to consider purchasing additional AAPL shares while also evaluating your portfolio for diversification opportunities to ensure balanced risk management.');
    }, 1000); // Delay of 1 second
  };

  const line_chart_data = [
    { date: 'Start of Deal', price: 35.60 },
    { date: '1', price: 29.20 },
    { date: '2', price: 33.80 },
    { date: '3', price: 34.50 },
    { date: '4', price: 32.00 },
    { date: '5', price: 35.60 },
    { date: '6', price: 36.20 },
    { date: '7', price: 36.80 },
    { date: '8', price: 42.40 },
    { date: '9', price: 42.50 },
    { date: '10', price: 38.60 },
    { date: '11', price: 40 },
  ];

  return (
    <Container sx={{ marginTop: 10 }}>
      <Typography variant="h4" align="center">
        <img src={appleLogo} alt="Apple Logo" style={{ width: 40, height: 45, verticalAlign: 'middle', marginRight: 10, paddingBottom: 8 }} />
        Apple Inc. (AAPL)
      </Typography>
      <Typography variant="h6" align="center" color="textSecondary">Exchange (NASDAQ)</Typography>

      <Grid container spacing={3} sx={{ marginTop: 3 }}>
        <Grid item xs={12} sm={4}>
          <Card sx={{ padding: 2 }}>
            <Typography variant="body1" color="textSecondary">Share Price</Typography>
            <Typography variant="h5" textAlign="center" fontWeight="bold">$40.00</Typography>
          </Card>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Card sx={{ padding: 2 }}>
            <Typography variant="body1" color="textSecondary">Client Average Cost Basis</Typography>
            <Typography variant="h5" textAlign="center" fontWeight="bold">$32.60</Typography>
          </Card>
        </Grid>
        <Grid item xs={12} sm={4}>
          <Card sx={{ padding: 2 }}>
            <Typography variant="body1" color="textSecondary">Client's Current Shares</Typography>
            <Typography variant="h5" textAlign="center" fontWeight="bold">1,000</Typography>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3} sx={{ marginTop: 0 }}>
        <Grid item xs={6} sm={6}>
          <Card sx={{ padding: 0 }}>
            <CardContent>
              <Typography variant="body1" gutterBottom>Total Profit / Losses</Typography>
              <Typography variant="h5" textAlign="center" fontWeight="bold" color="green">
                +$7,400
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={6} sm={6}>
          <Card sx={{ padding: 0 }}>
            <CardContent>
              <Typography variant="body1" gutterBottom>PE Ratio</Typography>
              <Typography variant="h5" textAlign="center" fontWeight="bold" color="#9b870c">
                33.18
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3} sx={{ marginTop: 0, marginBottom: 5 }}>
        <Grid item xs={12} sm={6}>
          <Card sx={{ marginTop: 0, height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>AAPL Stock Price Over the Last 12 Months</Typography>
              <ResponsiveContainer width="100%" height={390}>
              <LineChart
                data={line_chart_data}
                margin={{
                  top: 20, right: 30, left: 20, bottom: 5,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis label={{ value: 'Share Price', angle: -90, position: 'insideLeft' }} domain={[30, 45]} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="price" stroke="#FF3621" strokeWidth={2} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6}>
          <Card sx={{ padding: 2, marginTop: 0, backgroundColor: 'white', borderRadius: 2, boxShadow: 3, height: '100%', backgroundColor: 'rgba(255, 54, 33, 0.1)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', marginBottom: 2 }}>
                <img src={databricksLogo} alt="Databricks Logo" style={{ width: 32, height: 32, marginRight: 8 }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold' }}>Your AI Assistant's AAPL Summary</Typography>
              </Box>
              <Box sx={{ marginBottom: 2, backgroundColor: 'white', borderRadius: 1, padding: 2 }}>
                <ReactMarkdown>{summaryText}</ReactMarkdown>
              </Box>
              <Button
                variant="contained"
                color="primary"
                fullWidth
                onClick={regenerateSummary}
                startIcon={<img src={databricksLogo} alt="Databricks Logo" style={{ width: 24, height: 24 }} />}
                sx={{ fontWeight: 'bold', marginTop: 1, backgroundColor: 'white', color: 'black' }} // Added marginTop for spacing
              >
                Regenerate Summary
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <hr></hr>
      <Typography variant="h5" sx={{ marginTop: 3, fontWeight: 'bold' }}>Market News</Typography>
      <Typography variant="subtitle1" sx={{ marginBottom: 3, fontStyle: "italic" }}>Summarized from 1000s of Sources on Databricks</Typography>
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', maxWidth: 800, margin: 'auto', marginTop: 2 }}>
        <Grid container spacing={3} sx={{ marginTop: 1 }}>
          {getVisibleNews().map((news, index) => (
            <Grid item xs={12} sm={4} key={index}>
              <Card>
                <CardContent>
                  <Avatar src={news.icon} alt={news.title} sx={{ width: 32, height: 32, marginBottom: 1 }} />
                  <Typography variant="h6">{news.title}</Typography>
                  <Typography variant="body2" color="textSecondary">{news.description}</Typography>
                  <Button 
                    variant="outlined" 
                    size="small" 
                    startIcon={<img src={databricksLogo} alt="Databricks Logo" style={{ width: 24, height: 24 }} />}
                    sx={{ marginTop: 1 }}
                    onClick={news.title === 'Reddit' ? handleSummarizeClick : null}
                    disabled={news.title !== 'Reddit'}
                  >
                    Summarize
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
        <MobileStepper
          variant="dots"
          steps={maxSteps}
          position="static"
          activeStep={activeStep}
          sx={{ width: '100%', marginTop: 2 }}
          nextButton={
            <Button size="small" onClick={handleNext} disabled={activeStep === maxSteps - 1}>
              Next
              {theme.direction === 'rtl' ? <KeyboardArrowLeft /> : <KeyboardArrowRight />}
            </Button>
          }
          backButton={
            <Button size="small" onClick={handleBack} disabled={activeStep === 0}>
              {theme.direction === 'rtl' ? <KeyboardArrowRight /> : <KeyboardArrowLeft />}
              Back
            </Button>
          }
        />
      </Box>

      <hr></hr>

      <Typography variant="h5" sx={{ marginTop: 3, fontWeight: 'bold' }}>Existing reports and documents</Typography>
      <Typography variant="subtitle1" sx={{ marginBottom: 3, fontStyle: "italic" }}>Relevant PDF Documents</Typography>
      <Button variant="contained" color="secondary" sx={{ marginBottom: 2 }}>Upload a document</Button>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Sentiment</TableCell>
              <TableCell></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {reports.map((report, index) => (
              <TableRow key={report.name}>
                <TableCell>{report.name}</TableCell>
                <TableCell>{report.type}</TableCell>
                <TableCell 
                  sx={{ 
                    color: (() => {
                      const match = report.sentiment.match(/(\d+)%/); // Extract the number before '%'
                      const sentimentValue = match ? parseInt(match[1], 10) : 0;
                      return sentimentValue >= 40 && sentimentValue <= 60 ? "#CD7F32" : "#00A972";
                    })(), 
                    fontWeight: "bold" 
                  }}
                >
                  {report.sentiment}
                </TableCell>
                <TableCell>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => {
                      window.scrollTo(0, 0);
                      if (index === 0) {
                        navigate(`/reports/${report.name.replace(' ', '-')}`);
                      }
                    }}
                    disabled={index !== 0}
                  >
                    See details
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Container>
  );
}

export default DetailView;
