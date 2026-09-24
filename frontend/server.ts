import express from 'express';
import path from 'path';
import { randomUUID } from 'crypto';
import { createServer as createViteServer } from 'vite';
import dotenv from 'dotenv';

dotenv.config();

const SERVICE = 'carbonguard-dashboard-proxy';
const PORT = Number(process.env.PORT ?? process.env.FRONTEND_PORT ?? 3000);
const WEBHOOK_URL = process.env.SUPERFLOW_WEBHOOK_URL ?? 'https://inference.studio.lyzr.ai/api/workflows/execute';
const API_KEY = process.env.SUPERFLOW_API_KEY ?? process.env.LYZR_API_KEY;
const WORKFLOW_ID = process.env.WORKFLOW_ID ?? process.env.SUPERFLOW_WORKFLOW_ID;

function log(level: string, event: string, fields: Record<string, unknown> = {}) {
  console.log(JSON.stringify({
    timestamp: new Date().toISOString(),
    level,
    service: SERVICE,
    event,
    ...fields,
  }));
}

async function startServer() {
  const app = express();
  app.disable('x-powered-by');
  app.use(express.json({ limit: '256kb' }));

  app.use((req, res, next) => {
    const requestId = (req.header('X-Request-ID') || randomUUID()).slice(0, 128);
    const started = performance.now();
    res.setHeader('X-Request-ID', requestId);
    res.on('finish', () => log('INFO', 'request_completed', {
      request_id: requestId,
      method: req.method,
      path: req.path,
      status_code: res.statusCode,
      duration_ms: Number((performance.now() - started).toFixed(2)),
    }));
    (req as any).requestId = requestId;
    next();
  });

  app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', service: SERVICE, request_id: (req as any).requestId });
  });

  app.get('/api/ready', (req, res) => {
    const ready = Boolean(WEBHOOK_URL && WORKFLOW_ID);
    res.status(ready ? 200 : 503).json({
      status: ready ? 'ready' : 'not_ready',
      service: SERVICE,
      request_id: (req as any).requestId,
      upstream_configured: Boolean(WEBHOOK_URL),
      workflow_configured: Boolean(WORKFLOW_ID),
    });
  });

  app.post(['/api/superflow/execute', '/api/workflows/execute'], async (req, res) => {
    const requestId = (req as any).requestId as string;
    if (!WORKFLOW_ID) {
      return res.status(503).json({
        status: 'ERROR',
        error_code: 'WORKFLOW_NOT_CONFIGURED',
        message: 'SuperFlow workflow is not configured.',
        request_id: requestId,
      });
    }

    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Request-ID': requestId,
      };

      if (API_KEY) {
        headers['x-api-key'] = API_KEY;
        headers['Authorization'] = `Bearer ${API_KEY}`;
      }

      // The workflow ID is server-controlled and is deliberately applied last.
      // Client input cannot reroute execution to another workflow.
      const outboundBody = {
        ...req.body,
        workflow_id: WORKFLOW_ID,
        inputs: req.body,
      };

      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 30000);

      let response: Response;
      try {
        response = await fetch(WEBHOOK_URL, {
          method: 'POST',
          headers,
          body: JSON.stringify(outboundBody),
          signal: controller.signal,
        });
      } finally {
        clearTimeout(timeout);
      }

      const responseText = await response.text();
      let responseData: unknown;
      try {
        responseData = JSON.parse(responseText);
      } catch {
        responseData = { response: responseText };
      }

      return res.status(response.status).json(responseData);
    } catch (err: any) {
      const isTimeout = err?.name === 'AbortError';
      log('ERROR', 'superflow_proxy_error', {
        request_id: requestId,
        error_code: isTimeout ? 'UPSTREAM_TIMEOUT' : 'UPSTREAM_ERROR',
      });
      return res.status(502).json({
        status: 'ERROR',
        error_code: isTimeout ? 'UPSTREAM_TIMEOUT' : 'UPSTREAM_ERROR',
        message: isTimeout
          ? 'SuperFlow request timed out.'
          : 'Failed to communicate with SuperFlow.',
        request_id: requestId,
      });
    }
  });

  app.use((err: any, req: express.Request, res: express.Response, _next: express.NextFunction) => {
    log('ERROR', 'unhandled_http_error', { request_id: (req as any).requestId, error_code: 'INTERNAL_ERROR' });
    res.status(500).json({
      status: 'ERROR',
      error_code: 'INTERNAL_ERROR',
      message: 'Internal server error.',
      request_id: (req as any).requestId,
    });
  });

  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    log('INFO', 'server_started', { port: PORT });
  });
}

startServer().catch((error) => {
  log('ERROR', 'server_start_failed', { error_code: 'STARTUP_FAILURE' });
  process.exit(1);
});
