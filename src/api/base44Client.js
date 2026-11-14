import { createClient } from '@base44/sdk';
import { appParams } from '@/lib/app-params';

const { appId, token, functionsVersion, appBaseUrl } = appParams;

// When deployed off base44's own hosting (e.g. on Vercel at teraqub.com), the
// SDK still needs to call base44's API. Empty string makes the SDK target
// the current origin, which 404s here. Override via env if needed, else
// fall back to base44's production API.
const serverUrl = import.meta.env.VITE_BASE44_SERVER_URL || 'https://base44.app';

//Create a client with authentication required
export const base44 = createClient({
  appId,
  token,
  functionsVersion,
  serverUrl,
  requiresAuth: false,
  appBaseUrl
});
