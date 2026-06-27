const ALLOWED = new Set(['correlationId', 'route', 'status', 'durationMs', 'dependency', 'outcome']);

export function safeTelemetry(fields) {
  const result = {};
  for (const [key, value] of Object.entries(fields)) {
    if (ALLOWED.has(key)) result[key] = value;
  }
  return result;
}
