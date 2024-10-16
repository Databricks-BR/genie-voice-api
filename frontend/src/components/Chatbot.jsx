import React, { useState, useEffect, useRef } from "react";
import {
  Drawer,
  Container,
  Grid,
  Box,
  TextField,
  Button,
  IconButton,
  Typography,
  Paper,
  Avatar,
} from "@mui/material";

import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import MicRecorder from 'mic-recorder-to-mp3';
import FiberManualRecordIcon from '@mui/icons-material/FiberManualRecord';
import MicIcon from '@mui/icons-material/Mic';

import { useTheme } from '@mui/material/styles';
import { keyframes, styled } from "@mui/system";
import { Link } from "react-router-dom";
import axios from "axios";
import ReactMarkdown from 'react-markdown';
import ali_pic from "../assets/ali.jpg";
import databricks_small from "../assets/databricks_small.png";
import { useChatbot } from './ChatbotContext';
//import AudioRecorder from './AudioRecorder';
import BrainIcon from '@mui/icons-material/EmojiObjects'; // Import a suitable icon
import CloudUploadIcon from "@mui/icons-material/CloudUpload";

const ChatContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  backgroundColor: "#F9F7F4",
  height: "100%",
  display: "flex",
  flexDirection: "column",
  justifyContent: "space-between",
  width: "850px",
}));

const ChatMessages = styled(Box)(({ theme }) => ({
  flexGrow: 1,
  overflowY: "auto",
  paddingRight: theme.spacing(1),
  display: "flex",
  flexDirection: "column",
  maxHeight: "calc(100% - 120px)",
}));

const MessageWrapper = styled(Box)(({ fromUser }) => ({
  display: "flex",
  flexDirection: fromUser ? "row-reverse" : "row",
  alignItems: "center",
  marginBottom: "16px",
}));

const MessageBubble = styled(Paper)(({ theme, fromUser }) => ({
  padding: theme.spacing(1.5),
  backgroundColor: fromUser
    ? theme.palette.primary.main
    : theme.palette.secondary.main,
  color: fromUser
    ? theme.palette.primary.contrastText
    : theme.palette.secondary.contrastText,
  maxWidth: "75%",
  borderRadius: fromUser ? "15px 15px 0 15px" : "15px 15px 15px 0",
  boxShadow: theme.shadows[3],
}));

const MessageInput = styled(Box)(({ theme }) => ({
  display: "flex",
  alignItems: "center",
  marginTop: theme.spacing(2),
  padding: theme.spacing(1),
  backgroundColor: "#F9F7F4",
  position: "fixed",
  bottom: 0,
  width: '800px',
}));

function Chatbot({ open, onClose }) {
  const { prefilledMessage, context, suggestion, setSuggestion, conversationId, setConversationId } = useChatbot();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState(prefilledMessage);
  const messagesEndRef = useRef(null);
  const [isAudioResponse, setIsAudioResponse] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recorder, setRecorder] = useState(null);
  const [player, setPlayer] = useState(null);
  const [audioFile, setAudioFile] = useState(null);
  const [permission, setPermission] = useState(false);
  const [stream, setStream] = useState(null);
  const [recordingStatus, setRecordingStatus] = useState("inactive");
  const [audioFileBase64, setAudioBase64] = useState(null);
  
  let token = localStorage.getItem("token");
  let spaceId = localStorage.getItem("spaceId");
  let keywordsGenie = localStorage.getItem("keywordsGenie");

  if (conversationId.length === 0) {
    setConversationId("0")
  }

  useEffect(() => {
    setInput(prefilledMessage);
  }, [prefilledMessage]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth"});
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const simulateStreamingResponse = (responseText, audio) => {
    const words = responseText.split(' '); // Split the response text into words
    let currentIndex = 0;
    let displayedText = "";
  
    const interval = 50;
  
    const streamInterval = setInterval(() => {
      if (currentIndex < words.length) {
        displayedText += (displayedText ? " " : "") + words[currentIndex];
        currentIndex += 1;
  
        if (!audio) {
          setMessages((prevMessages) => [
            ...prevMessages.slice(0, -1),
            { text: displayedText, fromUser: false },
          ]);
        } else {
          setMessages((prevMessages) => [
            ...prevMessages.slice(0, -1),
            { text: "🎤 " + displayedText, fromUser: true },
          ]);
        };
  
        // Scroll to bottom after every 10 words
        if (currentIndex % 10 === 0 || currentIndex === words.length) {
          scrollToBottom();
        }
        
      } else {
        clearInterval(streamInterval);
      }
    }, interval);
  };

  const AudioRecorder = () => {
    const reader = new FileReader();

    const startRecording = async () => {
      const newRecorder = new MicRecorder({ bitRate: 128 });
      
      if ("MediaRecorder" in window) {
        try {
            const streamData = await navigator.mediaDevices.getUserMedia({
                audio: true,
                video: false,
            });
            setPermission(true);
            setStream(streamData);
        } catch (err) {
            alert(err.message);
        }
      } else {
          alert("The MediaRecorder API is not supported in your browser.");
      }

      try {
        await newRecorder.start();
        setIsRecording(true);
        setRecorder(newRecorder);
        setRecordingStatus("recording")
      } catch (e) {
        console.error(e);
        alert(e)
      }
    };

    const stopRecording = async () => {
      if (!recorder) return;
      
      try {
        const [buffer, blob] = await recorder.stop().getMp3();
        const audioFile = new File(buffer, "voice-message.mp3", {
            type: blob.type,
            lastModified: Date.now(),
        });

        setPlayer(new Audio(URL.createObjectURL(audioFile)));
        setIsRecording(false);
        setAudioFile(audioFile); // Add this line
        setRecordingStatus("inactive")

        onStop(audioFile);

      } catch (e) {
        console.error(e);
        alert(e)
      }
    };

    const onStop = async (blob) => {

      reader.onloadend = async () => {
          
          try {
            const response = await axios.post(`${process.env.REACT_APP_API_URL}/chat_audio/`, {
              audio: reader.result,
              chat_history: messages.map((msg) => [msg.text, msg.fromUser ? "user" : "bot"])
            });          
            
            setMessages((prevMessages) => [
              ...prevMessages,
              { text: "", fromUser: true },
            ]);                       
                       
            simulateStreamingResponse(response.data.response, true);
            handleSendAudioTranscript(response.data.response);
  
          } catch (error) {
            console.error("Error uploading audio file:", error);
            
            setMessages((prevMessages) => [
              ...prevMessages,
              { text: "Estamos com problemas ao fazer o transcript do audio. Favor usar o audio em alguns minutos.", fromUser: false },
            ]);                       
            
            simulateStreamingResponse("Estamos com problemas ao fazer o transcript do audio. Favor usar o audio em alguns minutos.", true);
          }
        }
      
      reader.readAsDataURL(blob);        
      
    };

    return (
            <Grid container spacing={1} justifyContent="left">
              {!isRecording ? (
                <Grid item>
                      <IconButton
                        color="secondary"
                        aria-label="start recording"
                        onClick={startRecording}
                        disabled={isRecording}
                        >
                        <MicIcon sx={{ fontSize: 40, marginBottom: 1,  marginLeft: 1 }} />
                      </IconButton>
                  </Grid>
              ) : (
                <Grid item>
                      <IconButton
                        color="primary"
                        aria-label="start recording"
                        onClick={stopRecording}
                        disabled={!isRecording}
                        >
                        <MicIcon sx={{ fontSize: 40, marginBottom: 1,  marginLeft: 1 }} />
                      </IconButton>
                  </Grid>
              )}
            </Grid>
    )
  };

  const handleSendAudioTranscript = async (audioTranscript) => {
  
    // send audio transcript to bot          
    try {
      const response = await axios.post(`${process.env.REACT_APP_API_URL}/chat/`, {
        token: token,
        space_id: spaceId,
        keywords_genie: keywordsGenie,
        conversation_id: conversationId,
        text: audioTranscript,
        chat_history: messages.map((msg) => [msg.text, "bot"])
      });
  
      const botResponse = response.data.response;
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: "", fromUser: false },
      ]);
  
      if (response.data.conversation_id) {
        setConversationId(response.data.conversation_id);
      } else {
        setConversationId("0");
      }      

      simulateStreamingResponse(botResponse, false);  

    } catch (error) {
      console.error("Error sending message:", error);
    }
  };

  const handleSend = async () => {
    if (input.trim() === "") return;
    const newMessages = [...messages, { text: input, fromUser: true }];
    
    setMessages(newMessages);
    setInput("");
    console.log(keywordsGenie);

    try {
      const response = await axios.post(`${process.env.REACT_APP_API_URL}/chat/`, {
        token: token,
        space_id: spaceId,
        keywords_genie: keywordsGenie,
        conversation_id: conversationId,
        text: input,
        chat_history: messages.map((msg) => [msg.text, msg.fromUser ? "user" : "bot"])
      });
  
      const botResponse = response.data.response;
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: "", fromUser: false }, // Placeholder for the streaming effect
      ]);
  
      simulateStreamingResponse(botResponse, false); // Simulate the streaming of the response
  
      if (response.data.suggestion) {
        setSuggestion(response.data.suggestion);
      } else {
        setSuggestion(null);
      }

      if (response.data.conversation_id) {
        setConversationId(response.data.conversation_id);
      } else {
        setConversationId("0");
      }      
  
    } catch (error) {
      console.error("Error sending message:", error);
    }
  };

  const handleClear = () => {
    setMessages([]);
    setSuggestion(null);  // Clear suggestion when messages are cleared
  };

  const handleAudio = async () => {
    AudioRecorder();   
  };

  const handleSuggestionClick = () => {
    setInput(suggestion);
    setSuggestion(""); // Clear the suggestion after clicking
  };

  
  return (
    <Drawer anchor="left" open={open} onClose={onClose}>
      <Box sx={{ padding: 2, backgroundColor: "#F9F7F4" }}>
        <Typography variant="h4" align="center">
          AI Assistant
        </Typography>
        <Link to="https://docs.databricks.com/en/generative-ai/generative-ai.html">
          <Typography variant="h6" align="center" sx={{ color: "#FF3621" }}>
            GenAI Powered
          </Typography>
        </Link>
        {context && (
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', marginLeft: 2, marginRight: 2, padding: 1, backgroundColor: '#00A972', borderRadius: 1, marginTop: 1 }}>
            <BrainIcon sx={{ color: "#FFFFFF", marginRight: 1 }} />
            <Typography variant="body2" align="center" sx={{ color: "#FFFFFF" }}>
              Usando <span style={{ fontWeight: 'bold' }}>{context}</span>
            </Typography>
          </Box>
        )}
        <hr />
      </Box>
      <ChatContainer>
        <ChatMessages>
        {messages.map((message, index) => (
            <MessageWrapper 
              key={index} 
              fromUser={message.fromUser} 
              sx={{ display: 'flex', alignItems: 'flex-end' }}
            >
              <Avatar 
                src={message.fromUser ? ali_pic : databricks_small} 
                alt="User Avatar" 
                sx={{ marginRight: message.fromUser ? 2 : 0, marginLeft: message.fromUser ? 0 : 2 }}  // Adjust margin to control spacing
              />
              <MessageBubble fromUser={message.fromUser}>
                <Typography variant="body1">
                  <ReactMarkdown>{message.text}</ReactMarkdown>
                </Typography>
              </MessageBubble>
            </MessageWrapper>
          ))}
          <div ref={messagesEndRef} />
        </ChatMessages>
        {suggestion && (
          <Button
            variant="outlined"
            color="primary"
            sx={{ 
              marginBottom: 10, 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'flex-start', 
              textAlign: 'left' 
            }}
            onClick={handleSuggestionClick}
          >
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <img src={databricks_small} alt="Databricks Logo" style={{ width: 24, height: 24, marginRight: 8 }} />
              <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
              Suggested Questions:
              </Typography>
            </Box>
            <Typography variant="body2" sx={{ marginTop: 1 }}>
              {suggestion}
            </Typography>
          </Button>
        )}
        <MessageInput>
        <TextField
            fullWidth
            multiline
            maxRows={4}
            variant="outlined"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault(); // Prevents the default action of inserting a newline
                handleSend(); // Sends the message
              }
            }}
            sx={{
              "& .MuiOutlinedInput-root": {
                "& fieldset": {
                  borderColor: "#FF3621",
                },
                "&:hover fieldset": {
                  borderColor: "#FF3621",
                },
                "&.Mui-focused fieldset": {
                  borderColor: "#FF3621",
                },
                width: "550px",
                height: "65px",
                backgroundColor: "#FFFFFF",
                borderRadius: '8px',                
              },
            }}
          />
          <Button
            variant="contained"
            color="primary"
            onClick={handleSend}
            sx={{ marginBottom: 1, marginLeft: 70, height: "56px" }}
          >
            Send
          </Button>
          <Button
            variant="outlined"
            color="secondary"
            onClick={handleClear}
            sx={{marginBottom: 1,  marginLeft: 1, height: "56px" }}
          >
            Clear
          </Button>
        
          <AudioRecorder
            isAudioResponse={isAudioResponse}
            onClick={handleAudio}
          />

        </MessageInput>
      </ChatContainer>
    </Drawer>
  );
}

export default Chatbot;