const defaultBase = typeof window !== "undefined" 
  ? (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000") 
  : "http://localhost:8000";

export async function api<T>(
  path: string,
  opts?: RequestInit & { base?: string }
): Promise<T> {
  const base = opts?.base ?? defaultBase;
  const { base: _, ...rest } = opts ?? {};
  const res = await fetch(`${base}${path}`, {
    ...rest,
    headers: { "Content-Type": "application/json", ...rest.headers },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? res.statusText);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}
