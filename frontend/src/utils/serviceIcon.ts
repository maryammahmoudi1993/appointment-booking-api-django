import { ScissorsIcon, SparklesIcon, HandIcon, LotusIcon, FlameIcon } from "../components/icons/ServiceIcons";

export function iconForService(name: string) {
  const lower = name.toLowerCase();
  if (lower.includes("hair") || lower.includes("color")) return ScissorsIcon;
  if (lower.includes("facial") || lower.includes("skin")) return SparklesIcon;
  if (lower.includes("nail") || lower.includes("manicure") || lower.includes("polish")) return HandIcon;
  if (lower.includes("massage") || lower.includes("spa") || lower.includes("relax")) return LotusIcon;
  return FlameIcon;
}
