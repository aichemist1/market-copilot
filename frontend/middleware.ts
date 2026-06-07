import { NextRequest, NextResponse } from "next/server";
import { decodeSession, SESSION_COOKIE_NAME } from "@/lib/auth-session";

const AUTH_FREE_PATHS = [
  "/login",
  "/register",
  "/api/auth/login",
  "/api/auth/register",
  "/api/auth/logout",
];
const ADMIN_ONLY_PREFIXES = ["/admin", "/alerts"];

function isProtectedPath(pathname: string) {
  if (
    pathname.startsWith("/_next") ||
    pathname.startsWith("/favicon") ||
    pathname.startsWith("/api/")
  ) {
    return false;
  }

  return true;
}

function buildExternalUrl(request: NextRequest, pathname: string) {
  const forwardedProto = request.headers.get("x-forwarded-proto");
  const forwardedHost = request.headers.get("x-forwarded-host");
  const forwardedPort = request.headers.get("x-forwarded-port");
  const url = request.nextUrl.clone();

  if (forwardedProto) {
    url.protocol = `${forwardedProto}:`;
  }

  if (forwardedHost) {
    url.host = forwardedHost;
  } else if (request.headers.get("host")) {
    url.host = request.headers.get("host") as string;
  }

  if (forwardedPort && forwardedHost && !forwardedHost.includes(":")) {
    url.host = `${forwardedHost}:${forwardedPort}`;
  }

  url.pathname = pathname;
  url.search = "";
  return url;
}

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (AUTH_FREE_PATHS.some((path) => pathname === path)) {
    const session = await decodeSession(request.cookies.get(SESSION_COOKIE_NAME)?.value);
    if ((pathname === "/login" || pathname === "/register") && session) {
      return NextResponse.redirect(buildExternalUrl(request, "/"));
    }
    return NextResponse.next();
  }

  if (!isProtectedPath(pathname)) {
    return NextResponse.next();
  }

  const session = await decodeSession(request.cookies.get(SESSION_COOKIE_NAME)?.value);
  if (!session) {
    const loginUrl = buildExternalUrl(request, "/login");
    loginUrl.searchParams.set("next", pathname + request.nextUrl.search);
    return NextResponse.redirect(loginUrl);
  }

  if (ADMIN_ONLY_PREFIXES.some((prefix) => pathname.startsWith(prefix)) && session.profile !== "admin") {
    return NextResponse.redirect(buildExternalUrl(request, "/"));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!.*\\..*).*)"],
};
