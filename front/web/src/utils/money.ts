export function fmtCents(cents: number, currency = "MXN"): string {
  return new Intl.NumberFormat("es-MX", {
    style: "currency",
    currency
  }).format(cents / 100);
}

export function parseAmountToCents(input: string): number {
  const value = Number(input.replace(/[$,\s]/g, ""));
  if (!Number.isFinite(value) || value <= 0) {
    throw new Error("Monto inválido");
  }
  return Math.round(value * 100);
}
