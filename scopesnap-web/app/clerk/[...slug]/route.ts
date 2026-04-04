/**
 * Clerk Proxy Route Handler
 *
 * Routes all Clerk API / ClerkJS requests through snapai.mainnov.tech/clerk/
 * so the custom Clerk subdomain (clerk.snapai.mainnov.tech) isn't required to
 * serve content from the browser.
 *
 * This is needed while Clerk's CDN finishes provisioning the custom domain.
 * Requests are forwarded to frontend-api.clerk.services with the correct
 * Host header so Clerk can identify the right application instance.
 */

import { NextRequest, NextResponse } from "next/server";

const CLERK_FRONTEND_API_HOST = "frontend-api.clerk.services";
const CLERK_CUSTOM_HOST = "clerk.snapai.mainnov.tech";

// Headers that should not be forwarded to/from Clerk
const HOP_BY_HOP = new Set([
  "connection",
  "keep-alive",
  "proxy-authenticate",
  "proxy-authorization",
  "te",
  "trailers",
  "transfer-encoding",
  "upgrade",
  "host", // We set this explicitly
]);

async function proxyRequest(
  request: NextRequest,
  slug: string[]
): Promise<NextResponse> {
  const path = slug.join("/");

  // Build target URL
  const targetUrl = new URL(
    `https://${CLERK_FRONTEND_API_HOST}/${path}`
  );

  // Forward query params
  request.nextUrl.searchParams.forEach((value, key) => {
    targetUrl.searchParams.set(key, value);
  });

  // Build forwarded headers — set Host so Clerk knows which instance this is
  const forwardHeaders: Record<string, string> = {
    host: CLERK_CUSTOM_HOST,
  };
  request.headers.forEach((value, key) => {
    if (!HOP_BY_HOP.has(key.toLowerCase())) {
      forwardHeaders[key] = value;
    }
  });

  // Forward request body for POST/PATCH/PUT
  let body: ArrayBuffer | undefined;
  if (!["GET", "HEAD", "OPTIONS"].includes(request.method)) {
    body = await request.arrayBuffer();
  }

  let response: Response;
  try {
    response = await fetch(targetUrl.toString(), {
      method: request.method,
      headers: forwardHeaders,
      body: body,
      // @ts-expect-error — undici supports duplex
      duplex: "half",
    });
  } catch (err) {
    console.error("[clerk-proxy] fetch error:", err);
    return NextResponse.json({ error: "Clerk proxy error" }, { status: 502 });
  }

  // Build response headers — forward everything except hop-by-hop
  const responseHeaders = new Headers();
  response.headers.forEach((value, key) => {
    if (!HOP_BY_HOP.has(key.toLowerCase())) {
      responseHeaders.set(key, value);
    }
  });
  // Allow browser to read Clerk's response (CORS for same-origin requests)
  responseHeaders.set("access-control-allow-origin", "*");

  const responseBody = await response.arrayBuffer();

  return new NextResponse(responseBody, {
    status: response.status,
    statusText: response.statusText,
    headers: responseHeaders,
  });
}

export async function GET(
  request: NextRequest,
  { params }: { params: { slug: string[] } }
) {
  return proxyRequest(request, params.slug);
}

export async function POST(
  request: NextRequest,
  { params }: { params: { slug: string[] } }
) {
  return proxyRequest(request, params.slug);
}

export async function PUT(
  request: NextRequest,
  { params }: { params: { slug: string[] } }
) {
  return proxyRequest(request, params.slug);
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: { slug: string[] } }
) {
  return proxyRequest(request, params.slug);
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { slug: string[] } }
) {
  return proxyRequest(request, params.slug);
}

export async function OPTIONS(
  request: NextRequest,
  { params }: { params: { slug: string[] } }
) {
  return proxyRequest(request, params.slug);
}
