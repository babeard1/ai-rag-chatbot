import React from 'react';
import { Container, Typography, Box, AppBar, Toolbar, Divider } from '@mui/material';
import { Chat as ChatIcon } from '@mui/icons-material';
import FileUpload from './components/FileUpload';
import ChatBox from './components/ChatBox';

function App() {
  const handleUploadSuccess = (uploadedFiles) => {
    console.log('Successfully uploaded:', uploadedFiles);
    // You could show a snackbar notification here if you want
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      {/* App bar */}
      <AppBar position="static" elevation={0}>
        <Toolbar>
          <ChatIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            RAG Knowledge Base Chatbot
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Main content */}
      <Container maxWidth="lg" sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 4, textAlign: 'center' }}>
          <Typography variant="h4" gutterBottom>
            Chat with Your Documents
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Upload PDFs and ask questions. Get answers with source citations.
          </Typography>
        </Box>

        {/* File upload section */}
        <FileUpload onUploadSuccess={handleUploadSuccess} />

        <Divider sx={{ my: 4 }} />

        {/* Chat section */}
        <ChatBox />
      </Container>
    </Box>
  );
}

export default App;