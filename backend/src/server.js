const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const axios = require('axios');

// Init dotenv
dotenv.config();

// Express app setup
const app = express();
app.use(cors());
app.use(express.json());

// ENV Variables (from Railway / .env)
const ANYTHINGLLM_URL = process.env.ANYTHINGLLM_URL;
const ANYTHINGLLM_API_KEY = process.env.ANYTHINGLLM_API_KEY;

// Healthcheck route
app.get('/api/health', (req, res) => {
  res.json({ status: '✅ Backend API is running' });
});

// List Workspaces (Proxy to AnythingLLM)
app.get('/api/workspaces', async (req, res) => {
  try {
    const response = await axios.get(`${ANYTHINGLLM_URL}/api/workspaces`, {
      headers: {
        Authorization: `Bearer ${ANYTHINGLLM_API_KEY}`
      }
    });
    res.json(response.data);
  } catch (error) {
    console.error('❌ Error fetching workspaces:', error.message);
    res.status(500).json({ error: 'Failed to fetch workspaces' });
  }
});

// Create Workspace (Proxy to AnythingLLM)
app.post('/api/workspaces', async (req, res) => {
  const { name, tags } = req.body;
  try {
    const response = await axios.post(`${ANYTHINGLLM_URL}/api/workspaces`, {
      name,
      tags
    }, {
      headers: {
        Authorization: `Bearer ${ANYTHINGLLM_API_KEY}`
      }
    });
    res.json(response.data);
  } catch (error) {
    console.error('❌ Error creating workspace:', error.message);
    res.status(500).json({ error: 'Failed to create workspace' });
  }
});

// Server start
const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`✅ AnythingLLM Backend running on port ${PORT}`);
});

