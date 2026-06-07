import { LoginPage } from "@/components/login-page";

export default async function LoginRoute({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const resolved = await searchParams;
  const nextValue = resolved.next;
  const nextPath = Array.isArray(nextValue) ? nextValue[0] : nextValue;

  return <LoginPage nextPath={nextPath} />;
}
