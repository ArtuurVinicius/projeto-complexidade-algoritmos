const express = require('express');

const graphRoutes = require('./routes/graphRoutes');
const healthRoutes = require('./routes/healthRoutes');
const { swaggerUi, swaggerSpec } = require('./swagger');

const app = express();

app.use(express.json({ limit: '2mb' }));

app.use('/api', healthRoutes);
app.use('/api/graph', graphRoutes);
app.use('/api/docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));

app.use((req, res) => {
  res.status(404).json({ status: 'error', message: 'Not found' });
});

app.use((err, req, res, next) => {
  const status = Number.isInteger(err.statusCode) ? err.statusCode : 500;
  const message = err.message || 'Internal server error';
  console.error('Express error:', err && err.stack ? err.stack : err);
  res.status(status).json({ status: 'error', message });
});

module.exports = app;
