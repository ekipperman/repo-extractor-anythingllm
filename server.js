const express = require('express');
const app = express();
const port = process.env.PORT || 8080;

app.use(express.json());

app.get('/api/workspaces', (req, res) => {
  res.status(200).json({ status: 'ok', message: 'AnythingLLM is alive ??' });
});

app.listen(port, '0.0.0.0', () => {
  console.log(? AnythingLLM Backend running on port \);
});
