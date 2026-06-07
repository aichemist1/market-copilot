import { NextRequest, NextResponse } from "next/server";
import { decodeSession, SESSION_COOKIE_NAME } from "@/lib/auth-session";

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
    return JSON.parse(text) as Record<string, unknown> | Array<Record<string, unknown>>;
  } catch {
    return null;
  }
}

async function requireAdminSession(request: NextRequest) {
  const session = await decodeSession(request.cookies.get(SESSION_COOKIE_NAME)?.value);
  if (!session) {
    return NextResponse.json({ error: "authentication required" }, { status: 401 });
  }
  if (session.profile !== "admin") {
    return NextResponse.json({ error: "admin access required" }, { status: 403 });
  }
  return session;
}

export async function GET(request: NextRequest) {
  const session = await requireAdminSession(request);
  if (session instanceof NextResponse) {
    return session;
  }

  const upstream = await fetch(`${resolveApiBaseUrl()}/auth/invite-codes`, {
    headers: {
      "x-user-profile": session.profile,
      "x-user-email": session.email,
    },
    cache: "no-store",
  });

  const payload = await parseJsonResponse(upstream);
  if (!upstream.ok) {
    return NextResponse.json(
      {
        error:
          (payload && !Array.isArray(payload) && typeof payload.detail === "string")
            ? payload.detail
            : `upstream invite request failed with status ${upstream.status}`,
      },
      { status: upstream.status },
    );
  }

  return NextResponse.json({ inviteCodes: Array.isArray(payload) ? payload : [] });
}

export async function POST(request: NextRequest) {
  const session = await requireAdminSession(request);
  if (session instanceof NextResponse) {
    return session;
  }

  const body = await request.json();
  const upstream = await fetch(`${resolveApiBaseUrl()}/auth/invite-codes`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-user-profile": session.profile,
      "x-user-email": session.email,
    },
    body: JSON.stringify({
      expires_days: body.expiresDays ?? 14,
      code: body.code || null,
    }),
    cache: "no-store",
  });

  const payload = await parseJsonResponse(upstream);
  if (!upstream.ok) {
    return NextResponse.json(
      {
        error:
          (payload && !Array.isArray(payload) && typeof payload.detail === "string")
            ? payload.detail
            : `upstream invite request failed with status ${upstream.status}`,
      },
      { status: upstream.status },
    );
  }

  return NextResponse.json({ inviteCode: payload }, { status: upstream.status });
}
