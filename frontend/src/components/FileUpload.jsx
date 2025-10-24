import React, { useCallback, useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Box,
  Paper,
  Typography,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  CircularProgress,
  Alert,
  Divider,
  Chip,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Description as FileIcon,
  Delete as DeleteIcon,
  CheckCircle as SuccessIcon,
  Storage as KnowledgeIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { uploadDocument, listDocuments } from '../services/api';

const FileUpload = ({ onUploadSuccess }) => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [loadingDocuments, setLoadingDocuments] = useState(false);

  // Fetch existing documents on component mount
  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    setLoadingDocuments(true);
    try {
      const response = await listDocuments();
      setUploadedFiles(response.documents || []);
    } catch (err) {
      console.error('Failed to fetch documents:', err);
      // Don't show error to user, just log it
    } finally {
      setLoadingDocuments(false);
    }
  };

  // Handle file drop or selection
  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    setError(null);

    // Handle rejected files (wrong type, too large, etc.)
    if (rejectedFiles.length > 0) {
      const reasons = rejectedFiles.map(f => f.errors[0].message).join(', ');
      setError(`Some files were rejected: ${reasons}`);
    }

    // Add accepted files to the list
    setFiles(prevFiles => [...prevFiles, ...acceptedFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    maxSize: 10 * 1024 * 1024, // 10MB limit
    multiple: true,
  });

  // Remove a file from the list before uploading
  const removeFile = (fileToRemove) => {
    setFiles(files.filter(f => f !== fileToRemove));
  };

  // Upload all files
  const handleUpload = async () => {
    if (files.length === 0) return;

    setUploading(true);
    setError(null);
    const successfulUploads = [];

    try {
      // Upload each file sequentially
      for (const file of files) {
        try {
          const response = await uploadDocument(file);
          successfulUploads.push({
            name: file.name,
            ...response,
          });
        } catch (err) {
          console.error(`Failed to upload ${file.name}:`, err);
          setError(`Failed to upload ${file.name}: ${err.message}`);
          break; // Stop on first error
        }
      }

      if (successfulUploads.length > 0) {
        setFiles([]); // Clear the pending files
        
        // Refresh the document list from backend
        await fetchDocuments();
        
        // Notify parent component
        if (onUploadSuccess) {
          onUploadSuccess(successfulUploads);
        }
      }
    } catch (err) {
      setError(`Upload failed: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <Box>
      {/* Knowledge Base Status - Show this prominently at the top */}
      {uploadedFiles.length > 0 && (
        <Paper 
          elevation={2}
          sx={{ 
            mb: 3, 
            p: 2.5, 
            bgcolor: 'primary.light',
            color: 'primary.contrastText',
            border: 2,
            borderColor: 'primary.main',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
            <KnowledgeIcon sx={{ mr: 1.5, fontSize: 28 }} />
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Active Knowledge Base
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                Chatbot can answer questions from these documents
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip 
                label={`${uploadedFiles.length} document${uploadedFiles.length !== 1 ? 's' : ''}`}
                sx={{ 
                  bgcolor: 'white', 
                  color: 'primary.main',
                  fontWeight: 600,
                }}
              />
              <IconButton
                size="small"
                onClick={fetchDocuments}
                disabled={loadingDocuments}
                sx={{ 
                  color: 'white',
                  '&:hover': { bgcolor: 'rgba(255,255,255,0.2)' }
                }}
                title="Refresh document list"
              >
                {loadingDocuments ? <CircularProgress size={20} /> : <RefreshIcon />}
              </IconButton>
            </Box>
          </Box>
          
          <Divider sx={{ my: 1.5, bgcolor: 'white', opacity: 0.3 }} />
          
          <List dense disablePadding>
            {uploadedFiles
              .sort((a, b) => {
                // Natural sort - handles numbers correctly
                const nameA = (a.filename || a.name || '').toLowerCase();
                const nameB = (b.filename || b.name || '').toLowerCase();
                
                return nameA.localeCompare(nameB, undefined, {
                  numeric: true,
                  sensitivity: 'base'
                });
              })
              .map((file, index) => (
                <ListItem 
                  key={index}
                  sx={{ 
                    px: 0,
                    py: 0.5,
                  }}
                >
                  <ListItemIcon sx={{ minWidth: 32 }}>
                    <FileIcon sx={{ color: 'white', fontSize: 20 }} />
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Typography variant="body2" sx={{ fontWeight: 500 }}>
                        {file.filename || file.name}
                      </Typography>
                    }
                    secondary={
                      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                        {file.total_pages ? `${file.total_pages} pages • ` : ''}
                        {file.total_chunks || file.chunks_created || 'Unknown'} searchable chunks
                      </Typography>
                    }
                  />
                </ListItem>
              ))}
          </List>
        </Paper>
      )}

      {/* Drop zone */}
      <Paper
        {...getRootProps()}
        sx={{
          p: 4,
          textAlign: 'center',
          cursor: 'pointer',
          bgcolor: isDragActive ? 'action.hover' : 'background.paper',
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'divider',
          transition: 'all 0.3s',
          '&:hover': {
            borderColor: 'primary.main',
            bgcolor: 'action.hover',
          },
        }}
      >
        <input {...getInputProps()} />
        <UploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          {isDragActive ? 'Drop PDFs here...' : 'Drag & drop PDFs here'}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          or click to select files (max 10MB each)
        </Typography>
      </Paper>

      {/* Error message */}
      {error && (
        <Alert severity="error" sx={{ mt: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Pending files list */}
      {files.length > 0 && (
        <Paper sx={{ mt: 2, p: 2 }}>
          <Typography variant="subtitle1" gutterBottom>
            Files to upload ({files.length})
          </Typography>
          <List dense>
            {files.map((file, index) => (
              <ListItem
                key={index}
                secondaryAction={
                  <IconButton
                    edge="end"
                    onClick={() => removeFile(file)}
                    disabled={uploading}
                  >
                    <DeleteIcon />
                  </IconButton>
                }
              >
                <ListItemIcon>
                  <FileIcon color="primary" />
                </ListItemIcon>
                <ListItemText
                  primary={file.name}
                  secondary={`${(file.size / 1024 / 1024).toFixed(2)} MB`}
                />
              </ListItem>
            ))}
          </List>
          <Button
            variant="contained"
            fullWidth
            onClick={handleUpload}
            disabled={uploading}
            startIcon={uploading ? <CircularProgress size={20} /> : <UploadIcon />}
            sx={{ mt: 2 }}
          >
            {uploading ? 'Uploading...' : `Upload ${files.length} file(s)`}
          </Button>
        </Paper>
      )}
    </Box>
  );
};

export default FileUpload;