import serviceFacial from "../assets/landing/service-facial.webp";
import serviceHair from "../assets/landing/service-hair.webp";
import serviceHairColor from "../assets/landing/service-hair-color.webp";
import serviceManicure from "../assets/landing/service-manicure.webp";
import serviceMassage from "../assets/landing/service-massage.webp";
import serviceBeardTrim from "../assets/landing/service-beard-trim.webp";

export function imageForService(name: string): string {
  const lower = name.toLowerCase();
  if (lower.includes("beard")) return serviceBeardTrim;
  if (lower.includes("color")) return serviceHairColor;
  if (lower.includes("hair") || lower.includes("cut")) return serviceHair;
  if (lower.includes("facial") || lower.includes("skin")) return serviceFacial;
  if (lower.includes("nail") || lower.includes("manicure") || lower.includes("polish")) return serviceManicure;
  if (lower.includes("massage") || lower.includes("spa") || lower.includes("relax")) return serviceMassage;
  return serviceFacial;
}
