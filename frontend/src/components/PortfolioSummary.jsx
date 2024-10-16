import React, {  useRef } from "react";
import { Typography, Select, MenuItem, Box, Avatar, Card, CardContent, Button } from '@mui/material';
import ron_pic from '../assets/ron.jpg';
import databricksLogo from '../assets/databricks_small.png';
import { useChatbot } from './ChatbotContext';

const clientData = {
  'Sicoob': {
    name: 'Ron Gabrisko',
    image: ron_pic,
  },
  'Itaú Unibanco': {
    name: 'Ron Gabrisko',
    image: ron_pic,
  },
  'Caixa Econômica Federal': {
    name: 'Ron Gabrisko',
    image: ron_pic,
  }
};

function PortfolioSummary({ selectedAccount, setSelectedAccount, accountData }) {
  const { openChatbotWithSuggestion } = useChatbot();

  const handleChange = (event) => {
    setSelectedAccount(event.target.value);
  };

  const client = clientData[selectedAccount];
  const accountValue = accountData[selectedAccount].value;
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleAnalyzeClick = () => {
    openChatbotWithSuggestion("What is Open Finance?", "What is Open Finance?");
    // Add a small delay to ensure the chat is rendered before scrolling
    setTimeout(() => {
      scrollToBottom();
    }, 200); // Adjust the delay if necessary    
  };

  return (
    <Card sx={{ marginTop: 2 }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" textAlign="center" sx={{ flexDirection: { xs: 'column', sm: 'row' } }}>
          <Box display="flex" flexDirection="column" alignItems="center">
            <Avatar
              alt={client.name}
              src={client.image}
              sx={{ width: 80, height: 80, marginBottom: 1 }}
            />
            <Typography variant="h6">{client.name}</Typography>
          </Box>
          <Box display="flex" flexDirection="column" alignItems="center">
            <Typography variant="h4">Open Finance</Typography>
            <Box display="flex" flexDirection="column" alignItems="center">
              <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                $ {accountValue.toLocaleString()}
              </Typography>
            </Box>
          </Box>
          <Select
            value={selectedAccount}
            onChange={handleChange}
            displayEmpty
            sx={{ width: 220, height: 50, marginTop: 1, marginBottom: 1 }}
          >
            {Object.keys(accountData).map((account) => (
              <MenuItem key={account} value={account}>
                <em>{account}</em>
              </MenuItem>
            ))}
          </Select>
        </Box>
        <Box sx={{ display: 'flex', justifyContent: 'center', marginBottom: 1 }}>
          <Button
            variant="outlined"
            color="primary"
            startIcon={<img src={databricksLogo} alt="Databricks Logo" style={{ width: 24, height: 24 }} />}
            sx={{ width: '60%', backgroundColor: 'transparent' }}
            onClick={handleAnalyzeClick}
          >
          AI Assistant for Open Finance Data Analysis
          </Button>
        </Box>   
      </CardContent>
    </Card>
  );
}

export default PortfolioSummary;