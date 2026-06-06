export type AppUserProfile = "basic" | "premium" | "admin";

export type AppSession = {
  userId: string;
  email: string;
  profile: AppUserProfile;
};

export const SESSION_COOKIE_NAME = "market_copilot_session";

export function isAppUserProfile(value: unknown): value is AppUserProfile {
  return value === "basic" || value === "premium" || value === "admin";
}

function getSessionSecret() {
  return process.env.MARKET_COPILOT_SESSION_SECRET ?? "market-copilot-dev-session-secret";
}

function encodeBase64Url(input: Uint8Array) {
  let binary = "";
  input.forEach((value) => {
    binary += String.fromCharCode(value);
  });

  return btoa(binary)
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/g, "");
}

function decodeBase64Url(input: string) {
  const normalized = input.replace(/-/g, "+").replace(/_/g, "/");
  const padding = normalized.length % 4 === 0 ? "" : "=".repeat(4 - (normalized.length % 4));
  const binary = atob(`${normalized}${padding}`);
  return Uint8Array.from(binary, (character) => character.charCodeAt(0));
}

async function importSigningKey() {
  return crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(getSessionSecret()),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign", "verify"],
  );
}

export async function encodeSession(session: AppSession) {
  const payload = encodeBase64Url(
    new TextEncoder().encode(
      JSON.stringify({
        ...session,
        issuedAt: Date.now(),
      }),
    ),
  );
  const key = await importSigningKey();
  const signature = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(payload));
  return `${payload}.${encodeBase64Url(new Uint8Array(signature))}`;
}

export async function decodeSession(value: string | undefined): Promise<AppSession | null> {
  if (!value) {
    return null;
  }

  const [payload, signature] = value.split(".", 2);
  if (!payload || !signature) {
    return null;
  }

  const key = await importSigningKey();
  const verified = await crypto.subtle.verify(
    "HMAC",
    key,
    decodeBase64Url(signature),
    new TextEncoder().encode(payload),
  );

  if (!verified) {
    return null;
  }

  const parsed = JSON.parse(new TextDecoder().decode(decodeBase64Url(payload))) as AppSession & {
    issuedAt?: number;
  };

  if (!parsed.userId || !parsed.email || !parsed.profile) {
    return null;
  }

  return {
    userId: parsed.userId,
    email: parsed.email,
    profile: parsed.profile,
  };
}
