import { NextRequest, NextResponse } from "next/server";
import { SESSION_COOKIE_NAME, encodeSession } from "@/lib/auth-session";

const graphqlEndpoint =
  process.env.MARKET_COPILOT_GRAPHQL_ENDPOINT ?? "http://127.0.0.1:8000/graphql";

function resolveApiBaseUrl() {
  return process.env.MARKET_COPILOT_API_BASE_URL ?? graphqlEndpoint.replace(/\/graphql$/, "");
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

  const payload = await upstream.json();
  if (!upstream.ok) {
    return NextResponse.json(
      { error: payload.detail ?? "unable to sign in" },
      { status: upstream.status },
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
    secure: process.env.NODE_ENV === "production",
  });
  return response;
}
