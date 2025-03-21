const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');

// Init dotenv
dotenv.config();

// Express app setup
const app = express();
app.use(cors());
app.use(express.json());

// Healthcheck route
app.get('/api/health', (req, res) => {
  res.json({ status: 'Backend API is running ✅' });
});

// Workspaces API example
app.get('/api/workspaces', (req, res) => {
  // Replace with actual database query later
  res.json([{ id: 1, name: 'Workspace A' }, { id: 2, name: 'Workspace B' }]);
});

// Start server
const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`✅ AnythingLLM Backend running on port ${PORT}`);
});
