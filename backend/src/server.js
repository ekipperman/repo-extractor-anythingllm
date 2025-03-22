const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const axios = require('axios');

// ✅ Init dotenv to load environment variables
dotenv.config();

// ✅ Express app setup
const app = express();
app.use(cors());
app.use(express.json());

// ✅ ENV Variables (From Railway or .env)
const ANYTHINGLLM_URL = process.env.ANYTHINGLLM_URL;         // e.g. https://anythingllm-backend-production.up.railway.app/
const ANYTHINGLLM_API_KEY = process.env.ANYTHINGLLM_API_KEY; // Your AnythingLLM API Key

// ✅ Debug the ENV (Optional for Testing)
console.log('✅ ANYTHINGLLM_URL:', ANYTHINGLLM_URL);
console.log('✅ ANYTHINGLLM_API_KEY:', ANYTHINGLLM_API_KEY ? 'SET' : 'MISSING!');

// ✅ Healthcheck Route (Test your backend)
app.get('/api/health', (req, res) => {
  res.json({ status: '✅ Backend API is running' });
});

// ✅ Get Workspaces (Proxies to AnythingLLM Workspaces)
app.get('/api/workspaces', async (req, res) => {
  try {
    const response = await axios.get(`${ANYTHINGLLM_URL}/workspaces`, {
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

// ✅ Create a Workspace (Proxies to AnythingLLM)
app.post('/api/workspaces', async (req, res) => {
  const { name, tags } = req.body;

  try {
    const response = await axios.post(`${ANYTHINGLLM_URL}/workspaces`, {
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

// ✅ Start the Server
const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`✅ AnythingLLM Backend running on port ${PORT}`);
});
