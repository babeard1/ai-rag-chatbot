import React from 'react';
import { Box, Paper, Typography, Chip, Stack } from '@mui/material';
import { Person as UserIcon, SmartToy as BotIcon } from '@mui/icons-material';

const Message = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        mb: 2,
      }}
    >
      <Paper
        elevation={1}
        sx={{
          maxWidth: '70%',
          p: 2,
          bgcolor: isUser ? 'primary.main' : 'background.paper',
          color: isUser ? 'primary.contrastText' : 'text.primary',
        }}
      >
        {/* Message header with icon */}
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          {isUser ? (
            <UserIcon sx={{ mr: 1, fontSize: 20 }} />
          ) : (
            <BotIcon sx={{ mr: 1, fontSize: 20, color: 'primary.main' }} />
          )}
          <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
            {isUser ? 'You' : 'AI Assistant'}
          </Typography>
        </Box>

        {/* Message content */}
        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
          {message.content}
        </Typography>

        {/* Source citations (only for assistant messages) */}
        {/* {!isUser && message.sources && message.sources.length > 0 && (
          <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
            <Typography variant="caption" color="text.secondary" gutterBottom>
              Sources:
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              {message.sources.map((source, index) => (
                <Chip
                  key={index}
                  label={`${source.source} (p.${source.page})`}
                  size="small"
                  variant="outlined"
                  sx={{ mt: 0.5 }}
                />
              ))}
            </Stack>
          </Box>
        )} */}

        {!isUser && message.sources && message.sources.length > 0 && (
          <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
            <Typography variant="caption" color="text.secondary" gutterBottom>
              Sources:
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              {message.sources.map((source, index) => {
                // Handle undefined or missing page numbers
                const pageLabel = source.page !== undefined && source.page !== null 
                  ? `p.${source.page}` 
                  : 'page unknown';
                
                return (
                  <Chip
                    key={index}
                    label={`${source.source || 'Unknown'} (${pageLabel})`}
                    size="small"
                    variant="outlined"
                    sx={{ mt: 0.5 }}
                  />
                );
              })}
            </Stack>
          </Box>
        )}

      </Paper>
    </Box>
  );
};

export default Message;