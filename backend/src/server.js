const app = require('./app');

const parsedPort = Number(process.env.PORT);
const PORT = Number.isFinite(parsedPort) ? parsedPort : 3001;

app.listen(PORT, () => {
  console.log(`Graph API listening on port ${PORT}`);
});
