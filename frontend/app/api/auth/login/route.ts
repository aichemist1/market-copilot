import { NextRequest, NextResponse } from "next/server";
import {
  SESSION_COOKIE_NAME,
  encodeSession,
  isAppUserProfile,
  shouldUseSecureSessionCookie,
} from "@/lib/auth-session";

const graphqlEndpoint =
  process.env.MARKET_COPILOT_GRAPHQL_ENDPOINT ?? "http://127.0.0.1:8000/graphql";

function resolveApiBaseUrl() {
  return process.env.MARKET_COPILOT_API_BASE_URL ?? graphqlEndpoint.replace(/\/graphql$/, "");
}

async function parseJsonResponse(response: Response) {
  const text = await response.text();
  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text) as Record<string, unknown>;
  } catch {
    return null;
  }
}

export async function POST(request: NextRequest) {
  const { email, password } = (await request.json()) as {
    email?: string;
    password?: string;
  };

  if (!email || !password) {
    return NextResponse.json({ error: "email and password are required" }, { status: 400 });
  }

  const upstream = await fetch(`${resolveApiBaseUrl()}/auth/login`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
    },
    body: JSON.stringify({
      email,
      password,
    }),
    cache: "no-store",
  });

  const payload = await parseJsonResponse(upstream);
  if (!upstream.ok) {
    const upstreamDetail =
      typeof payload?.detail === "string"
        ? payload.detail
        : `upstream auth request failed with status ${upstream.status}`;
    return NextResponse.json(
      { error: upstreamDetail },
      { status: upstream.status },
    );
  }

  if (
    !payload ||
    typeof payload.user_id !== "string" ||
    typeof payload.email !== "string" ||
    !isAppUserProfile(payload.profile)
  ) {
    return NextResponse.json(
      { error: "auth service returned an unexpected response" },
      { status: 502 },
    );
  }

  const response = NextResponse.json({
    ok: true,
    profile: payload.profile,
  });
  response.cookies.set({
    name: SESSION_COOKIE_NAME,
    value: await encodeSession({
      userId: payload.user_id,
      email: payload.email,
      profile: payload.profile,
    }),
    httpOnly: true,
    path: "/",
    sameSite: "lax",
    secure: shouldUseSecureSessionCookie(),
  });
  return response;
}
