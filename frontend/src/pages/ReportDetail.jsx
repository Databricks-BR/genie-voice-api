import React from 'react';
import { Container, Typography, Button, Card, CardContent, Box, Avatar } from '@mui/material';
import { useParams } from 'react-router-dom';
import { Worker, Viewer } from '@react-pdf-viewer/core';
import '@react-pdf-viewer/core/lib/styles/index.css';
import samplePdf from '../assets/apple_q3_2023.pdf'; // Replace this with a path to an actual PDF
import ReactMarkdown from 'react-markdown';
import databricksLogo from '../assets/databricks_small.png'; // Make sure the path is correct
import { useChatbot } from '../components/ChatbotContext';

function ReportDetail() {
  const { reportName } = useParams();
  const { openChatbotWithMessage } = useChatbot();

  const markdownContent = `
  *In Apple's Q3 2023 earnings call, the company reported a record revenue in Services, reaching over 1 billion paid subscriptions, alongside strong iPhone sales in emerging markets, despite a slight year-over-year decline in overall revenue.* *Sources:*
  [1](https://www.apple.com/investor/earnings-call/), 
  [2](https://www.apple.com/newsroom/2023/08/apple-reports-third-quarter-results/), 
  [3](https://www.marketscreener.com/quote/stock/APPLE-INC-4849/calendar/).
  `;

  const handleAnalyzeClick = () => {
    openChatbotWithMessage("Analyze the AAPL Q3 2023 Earnings Call Transcript", "AAPL 2023 Earnings Call Transcript");
  };

  return (
    <Container sx={{ marginTop: 10 }}>
      <Typography variant="h4" align="center">Apple Inc. (AAPL)</Typography>
      <Typography variant="h6" align="center">{reportName ? reportName.replace('-', ' ') : ''}</Typography>
      
      <Box sx={{ backgroundColor: 'rgba(255, 54, 33, 0.1)', padding: 2, borderRadius: 2, display: 'flex', alignItems: 'center', marginBottom: 2, marginTop: 2 }}>
        <Avatar src={databricksLogo} alt="Databricks Logo" sx={{ marginRight: 2, width: 40, height: 40 }} />
        <Box>
          <Typography variant="h6" sx={{ color: 'primary.main', fontWeight: 'bold' }}>One-sentence Summary</Typography>
          <Typography variant="body1" sx={{ color: 'text.primary' }}>
            <ReactMarkdown>{markdownContent}</ReactMarkdown>
          </Typography>
        </Box>
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'center', marginBottom: 1, marginTop: 3 }}>
        <Button
          variant="outlined"
          color="primary"
          startIcon={<img src={databricksLogo} alt="Databricks Logo" style={{ width: 24, height: 24 }} />}
          sx={{ width: '60%', backgroundColor: 'transparent' }}
          onClick={handleAnalyzeClick}
        >
          Use Assistant to Analyze Document
        </Button>
      </Box>
      <Card sx={{ marginTop: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>Full PDF Document</Typography>
          <Box sx={{ height: '600px' }}>
            <Worker workerUrl="https://unpkg.com/pdfjs-dist@3.11.174/build/pdf.worker.min.js">
              <Viewer fileUrl={samplePdf} />
            </Worker>
          </Box>
        </CardContent>
      </Card>
    </Container>
  );
}

export default ReportDetail;