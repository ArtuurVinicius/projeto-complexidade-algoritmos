const express = require('express');

const router = express.Router();

// Simple healthcheck for frontend integration
router.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

module.exports = router;
