import React, { useEffect, useState } from 'react';
import {
  AppBar,
  Toolbar,
  Button,
  Avatar,
  Menu,
  MenuItem,
  Link as MuiLink,
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton,
  TextField,
  DialogActions,
  Typography,
  Box,
  Alert
} from '@mui/material';
import { Link } from 'react-router-dom';
import AccountBoxIcon from '@mui/icons-material/AccountBox';
import SettingsIcon from '@mui/icons-material/Settings';
import LogoutIcon from '@mui/icons-material/Logout';
import CloseIcon from '@mui/icons-material/Close';
import databricksLogo from '../assets/databricks.png';
import databricksIcon from '../assets/databricks_small.png';
import ali_pic from '../assets/ali.jpg';
import Chatbot from './Chatbot';
import { useChatbot } from './ChatbotContext';

function Header() {
  const { isOpen, openChatbotWithMessage, closeChatbot } = useChatbot();
  const [anchorEl, setAnchorEl] = useState(null);
  const [profileOpen, setProfileOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [token, setToken] = useState(null);
  const [spaceId, setSpaceId] = useState(null);
  const [keywordsGenie, setKeywordsGenie] = useState(null);
  
  // Toggle Chatbot Dialog
  const toggleChatbot = () => {
    if (isOpen) {
      closeChatbot();
    } else {
      openChatbotWithMessage('');
    }
  };

  // Handle Profile Menu Open
  const handleProfileMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  // Handle Profile Menu Close
  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  // Handle Profile Dialog Open
  const openProfileDialog = () => {
    setProfileOpen(true);
    handleProfileMenuClose();
  };

  // Handle Profile Dialog Close
  const closeProfileDialog = () => {
    setProfileOpen(false);
  };

  // Handle Settings Dialog Open
  const openSettingsDialog = () => {
    setSettingsOpen(true);
    handleProfileMenuClose();
  };

  // Handle Settings Dialog Close
  const saveSettingsDialog = () => {
    setToken(token);
    setSpaceId(spaceId);
    setKeywordsGenie(keywordsGenie);
    
    localStorage.setItem("token",token);
    localStorage.setItem("spaceId",spaceId);
    localStorage.setItem("keywordsGenie",keywordsGenie);

  };

  // Handle Settings Dialog Close
  const closeSettingsDialog = () => {
    setSettingsOpen(false);
  };

  const [email, setEmail] = useState('');


  useEffect(() => {
    // Function to fetch the email from the backend
    // const fetchEmail = async () => {
    //   try {
    //     const response = await fetch('/tracker'); // Adjust the URL if necessary
    //     const data = await response.json();
    //     setEmail(data.email);
    //   } catch (error) {
    //     console.error('Error fetching email:', error);
    //   }
    // };

    // fetchEmail();
  }, []);  

  return (
    <>
      <AppBar position="fixed" sx={{ backgroundColor: '#EDEDED', boxShadow: 'none' }}>
        <Toolbar>
          <Box display="flex" alignItems="center" flexGrow={1}>
            <Button variant="outlined" color="primary" sx={{ marginRight: 2 }} onClick={toggleChatbot} startIcon={<img src={databricksIcon} alt="Databricks Logo" style={{ width: 24, height: 24 }} />}>
              AI Assistant
            </Button>
            <Link to="/">
              <img src={databricksLogo} alt="Databricks Logo" style={{ height: '60px', marginRight: '10px' }} />
            </Link>
          </Box>
          <Box display="flex" alignItems="center">
            <Avatar
              alt="User Avatar"
              src={ali_pic}
              onClick={handleProfileMenuOpen}
              sx={{ cursor: 'pointer' }}
            />
            <Menu
              anchorEl={anchorEl}
              anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
              keepMounted
              transformOrigin={{ vertical: 'top', horizontal: 'right' }}
              open={Boolean(anchorEl)}
              onClose={handleProfileMenuClose}
            >
              <MenuItem onClick={openProfileDialog}>
                <AccountBoxIcon sx={{ marginRight: 1 }} />
                Profile
              </MenuItem>
              <MenuItem onClick={openSettingsDialog}>
                <SettingsIcon sx={{ marginRight: 1 }} />
                Settings
              </MenuItem>
              <MenuItem onClick={handleProfileMenuClose}>
                <LogoutIcon sx={{ marginRight: 1 }} />
                Logout
              </MenuItem>
            </Menu>
          </Box>
        </Toolbar>
      </AppBar>

      <Chatbot open={isOpen} onClose={closeChatbot} />

      <Dialog open={profileOpen} onClose={closeProfileDialog} fullWidth maxWidth="sm">
        <DialogTitle>
          Your Profile
          <IconButton
            aria-label="close"
            onClick={closeProfileDialog}
            sx={{
              position: 'absolute',
              right: 8,
              top: 8,
              color: (theme) => theme.palette.grey[500],
            }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent dividers>
          <Box display="flex" flexDirection="column" alignItems="center" mb={2}>
            <Avatar src={ali_pic} alt="Ali Ghodsi" sx={{ width: 100, height: 100, marginBottom: 2 }} />
            <Typography variant="h5">Ali Ghodsi</Typography>
            <Typography variant="subtitle1" color="textSecondary">Open Finance Analyst</Typography>
            <Typography variant="body2" color="textSecondary">ali@genaigenius.org</Typography>
          </Box>
          <TextField
            autoFocus
            margin="dense"
            id="name"
            value="Ali Ghodsi"
            label="Name"
            type="text"
            fullWidth
            variant="outlined"
            sx={{ marginBottom: 2 }}
          />
          <TextField
            margin="dense"
            id="email"
            value="ali@genaigenius.org"
            label="Email Address"
            type="email"
            fullWidth
            variant="outlined"
            sx={{ marginBottom: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={closeSettingsDialog} color="primary">
            Save
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={settingsOpen} onClose={closeSettingsDialog} fullWidth maxWidth="sm">
        <DialogTitle>
          Environment Settings
          <IconButton
            aria-label="close"
            onClick={closeSettingsDialog}
            sx={{
              position: 'absolute',
              right: 8,
              top: 8,
              color: (theme) => theme.palette.grey[500],
            }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent dividers>
          <TextField
            autoFocus
            margin="dense"
            id="token"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            label="Token"
            type="text"
            fullWidth
            variant="outlined"
            sx={{ marginBottom: 2 }}
          />
          <TextField
            margin="dense"
            id="spaceId"
            value={spaceId}
            onChange={(e) => setSpaceId(e.target.value)}
            label="Genie Space ID"
            type="text"
            fullWidth
            variant="outlined"
            sx={{ marginBottom: 2 }}
          />
          <TextField
            margin="dense"
            id="keywordsGenie"
            value={keywordsGenie}
            onChange={(e) => setKeywordsGenie(e.target.value)}
            label="Keywords for call Genie API."
            type="text"
            fullWidth
            variant="outlined"
            sx={{ marginBottom: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={saveSettingsDialog} color="primary">
            Save
          </Button>
          <Button onClick={closeSettingsDialog} color="secondary">
            Cancel
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

export default Header;