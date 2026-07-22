import serviceFacial from "../assets/landing/service-facial.webp";
import serviceHair from "../assets/landing/service-hair.webp";
import serviceManicure from "../assets/landing/service-manicure.webp";
import serviceMassage from "../assets/landing/service-massage.webp";

export function imageForService(name: string): string {
  const lower = name.toLowerCase();
  if (lower.includes("hair") || lower.includes("color")) return serviceHair;
  if (lower.includes("facial") || lower.includes("skin")) return serviceFacial;
  if (lower.includes("nail") || lower.includes("manicure") || lower.includes("polish")) return serviceManicure;
  if (lower.includes("massage") || lower.includes("spa") || lower.includes("relax")) return serviceMassage;
  return serviceFacial;
}
