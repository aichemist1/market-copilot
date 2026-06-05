import { NextRequest, NextResponse } from "next/server";

const graphqlEndpoint =
  process.env.MARKET_COPILOT_GRAPHQL_ENDPOINT ?? "http://127.0.0.1:8000/graphql";

export async function POST(request: NextRequest) {
  const body = await request.text();
  const userProfile = request.headers.get("x-user-profile") ?? "basic";

  const upstream = await fetch(graphqlEndpoint, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-user-profile": userProfile,
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
