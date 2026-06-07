import { RegisterPage } from "@/components/register-page";

export default async function RegisterRoute({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const resolved = await searchParams;
  const nextValue = resolved.next;
  const codeValue = resolved.code;
  const nextPath = Array.isArray(nextValue) ? nextValue[0] : nextValue;
  const inviteCode = Array.isArray(codeValue) ? codeValue[0] : codeValue;

  return <RegisterPage inviteCode={inviteCode} nextPath={nextPath} />;
}
