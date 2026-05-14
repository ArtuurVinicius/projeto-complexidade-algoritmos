function parseNumber(value) {
  if (value === undefined || value === null || value === '') {
    return null;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function validateNodePayload(body) {
  const errors = [];
  if (!body || typeof body !== 'object') {
    return { ok: false, errors: ['payload must be an object'] };
  }

  const id = typeof body.id === 'string' ? body.id.trim() : '';
  if (!id) {
    errors.push('id is required');
  }

  const lat = parseNumber(body.lat);
  const lon = parseNumber(body.lon);

  if (lat === null) {
    errors.push('lat must be a number');
  } else if (lat < -90 || lat > 90) {
    errors.push('lat must be between -90 and 90');
  }

  if (lon === null) {
    errors.push('lon must be a number');
  } else if (lon < -180 || lon > 180) {
    errors.push('lon must be between -180 and 180');
  }

  const name = typeof body.name === 'string' ? body.name : '';
  const type = typeof body.type === 'string' ? body.type : 'custom';

  return {
    ok: errors.length === 0,
    errors,
    value: {
      id,
      lat,
      lon,
      name,
      type,
    },
  };
}

function validateEdgePayload(body) {
  const errors = [];
  if (!body || typeof body !== 'object') {
    return { ok: false, errors: ['payload must be an object'] };
  }

  const from = typeof body.from === 'string' ? body.from.trim() : '';
  const to = typeof body.to === 'string' ? body.to.trim() : '';
  const mode = typeof body.mode === 'string' ? body.mode.trim() : '';

  if (!from) {
    errors.push('from is required');
  }
  if (!to) {
    errors.push('to is required');
  }
  if (!mode) {
    errors.push('mode is required');
  }

  const distanceM = parseNumber(body.distance_m);
  const timeS = parseNumber(body.time_s);

  if (distanceM === null || distanceM < 0) {
    errors.push('distance_m must be a number >= 0');
  }
  if (timeS === null || timeS < 0) {
    errors.push('time_s must be a number >= 0');
  }

  const cost = parseNumber(body.cost);
  const route = typeof body.route === 'string' ? body.route : '';

  return {
    ok: errors.length === 0,
    errors,
    value: {
      from,
      to,
      mode,
      distance_m: distanceM,
      time_s: timeS,
      cost: cost === null ? 0 : cost,
      route,
    },
  };
}

module.exports = {
  parseNumber,
  validateNodePayload,
  validateEdgePayload,
};
