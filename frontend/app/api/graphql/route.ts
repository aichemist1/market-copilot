import { NextRequest, NextResponse } from "next/server";
import { decodeSession, SESSION_COOKIE_NAME } from "@/lib/auth-session";

const graphqlEndpoint =
  process.env.MARKET_COPILOT_GRAPHQL_ENDPOINT ?? "http://127.0.0.1:8000/graphql";

export async function POST(request: NextRequest) {
  const session = await decodeSession(request.cookies.get(SESSION_COOKIE_NAME)?.value);
  if (!session) {
    return NextResponse.json({ errors: [{ message: "authentication required" }] }, { status: 401 });
  }

  const body = await request.text();

  const upstream = await fetch(graphqlEndpoint, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-user-profile": session.profile,
    },
    body,
    cache: "no-store",
  });

  const text = await upstream.text();

  return new NextResponse(text, {
    status: upstream.status,
    headers: {
      "content-type": "application/json",
    },
  });
}
