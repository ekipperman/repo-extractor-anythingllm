const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const axios = require('axios');

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

const ANYTHINGLLM_URL = process.env.ANYTHINGLLM_URL;
const ANYTHINGLLM_API_KEY = process.env.ANYTHINGLLM_API_KEY;

console.log('✅ ANYTHINGLLM_URL:', ANYTHINGLLM_URL);
console.log('✅ ANYTHINGLLM_API_KEY:', ANYTHINGLLM_API_KEY ? 'SET' : 'MISSING!');

// Healthcheck Route
app.get('/api/health', (req, res) => {
  res.json({ status: '✅ Backend API is running' });
});

// Get Workspaces Route
app.get('/api/workspaces', async (req, res) => {
  try {
    console.log('🔍 Calling AnythingLLM:', `${ANYTHINGLLM_URL}/workspaces`);

    const response = await axios.get(`${ANYTHINGLLM_URL}/workspaces`, {
      headers: {
        Authorization: `Bearer ${ANYTHINGLLM_API_KEY}`,
      },
    });

    console.log('✅ Workspaces fetched successfully:', response.data);
    res.json(response.data);
  } catch (error) {
    console.error('❌ Error fetching workspaces:', error.message);

    // Log more detail
    if (error.response) {
      console.error('❌ Error Response Data:', error.response.data);
      console.error('❌ Error Status:', error.response.status);
      console.error('❌ Error Headers:', error.response.headers);
      res.status(error.response.status).json({
        error: error.response.data || 'Failed to fetch workspaces',
      });
    } else if (error.request) {
      console.error('❌ No response received:', error.request);
      res.status(500).json({ error: 'No response received from AnythingLLM' });
    } else {
      console.error('❌ General Error:', error.message);
      res.status(500).json({ error: 'Failed to fetch workspaces' });
    }
  }
});

// Create Workspace Route
app.post('/api/workspaces', async (req, res) => {
  const { name, tags } = req.body;

  try {
    console.log('🔨 Creating workspace:', { name, tags });

    const response = await axios.post(
      `${ANYTHINGLLM_URL}/workspaces`,
      { name, tags },
      {
        headers: {
          Authorization: `Bearer ${ANYTHINGLLM_API_KEY}`,
        },
      }
    );

    console.log('✅ Workspace created:', response.data);
    res.json(response.data);
  } catch (error) {
    console.error('❌ Error creating workspace:', error.message);

    if (error.response) {
      console.error('❌ Error Response Data:', error.response.data);
      console.error('❌ Error Status:', error.response.status);
      console.error('❌ Error Headers:', error.response.headers);
      res.status(error.response.status).json({
        error: error.response.data || 'Failed to create workspace',
      });
    } else if (error.request) {
      console.error('❌ No response received:', error.request);
      res.status(500).json({ error: 'No response received from AnythingLLM' });
    } else {
      console.error('❌ General Error:', error.message);
      res.status(500).json({ error: 'Failed to create workspace' });
    }
  }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`✅ AnythingLLM Backend running on port ${PORT}`);
});
