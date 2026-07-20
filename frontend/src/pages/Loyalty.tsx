import { useEffect, useState } from "react";
import { loyaltyApi, type LoyaltyReward, type LoyaltySummary } from "../api/client";

export default function Loyalty() {
  const [summary, setSummary] = useState<LoyaltySummary | null>(null);
  const [rewards, setRewards] = useState<LoyaltyReward[]>([]);
  const [loading, setLoading] = useState(true);
  const [redeemingId, setRedeemingId] = useState<number | null>(null);
  const [error, setError] = useState("");

  const fetchAll = () => {
    setLoading(true);
    Promise.all([loyaltyApi.summary(), loyaltyApi.rewards()])
      .then(([summaryRes, rewardsRes]) => {
        setSummary(summaryRes.data);
        setRewards(rewardsRes.data.results);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const handleRedeem = async (reward: LoyaltyReward) => {
    setError("");
    setRedeemingId(reward.id);
    try {
      await loyaltyApi.redeem(reward.id);
      fetchAll();
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Could not redeem this reward right now."
      );
    } finally {
      setRedeemingId(null);
    }
  };

  if (loading || !summary) {
    return (
      <div className="flex justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-500 border-t-transparent" />
      </div>
    );
  }

  const nextReward = rewards
    .filter((r) => r.is_active && r.points_cost > summary.balance)
    .sort((a, b) => a.points_cost - b.points_cost)[0];
  const progress = nextReward
    ? Math.min(100, (summary.balance / nextReward.points_cost) * 100)
    : 100;

  return (
    <div className="mx-auto max-w-3xl px-4 py-14 sm:px-6 lg:px-8">
      <h2 className="font-display text-2xl font-bold text-brand-900">
        Loyalty Rewards
      </h2>
      <p className="mt-1 text-gray-600">Earn points with every visit.</p>

      <div className="mt-6 rounded-2xl bg-brand-700 p-6 text-white">
        <p className="text-xs font-medium uppercase tracking-wide text-brand-100">
          Your balance
        </p>
        <p className="mt-1 font-display text-4xl font-bold">
          {summary.balance} pts
        </p>
        <div className="mt-4 h-2 rounded-full bg-brand-900/40">
          <div
            className="h-2 rounded-full bg-white transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
        <p className="mt-2 text-xs text-brand-100">
          {nextReward
            ? `${nextReward.points_cost - summary.balance} pts to "${nextReward.name}"`
            : "You can redeem any reward in the catalog!"}
        </p>
      </div>

      {error && (
        <p className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">
          {error}
        </p>
      )}

      <h3 className="mt-8 text-xs font-semibold uppercase tracking-wide text-gray-500">
        Redeem a reward
      </h3>
      <div className="mt-3 space-y-3">
        {rewards.map((r) => {
          const canRedeem = r.is_active && summary.balance >= r.points_cost;
          return (
            <div
              key={r.id}
              className="flex items-center justify-between rounded-2xl border border-brand-100 bg-white p-4 shadow-sm"
            >
              <div>
                <p className="font-semibold text-gray-900">{r.name}</p>
                {r.description && (
                  <p className="text-sm text-gray-500">{r.description}</p>
                )}
                <p className="mt-1 text-sm font-medium text-brand-700">
                  {r.points_cost} pts
                </p>
              </div>
              <button
                onClick={() => handleRedeem(r)}
                disabled={!canRedeem || redeemingId === r.id}
                className="rounded-full bg-brand-600 px-4 py-1.5 text-xs font-semibold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:bg-gray-200 disabled:text-gray-400"
              >
                {redeemingId === r.id ? "Redeeming..." : "Redeem"}
              </button>
            </div>
          );
        })}
      </div>

      {summary.history.length > 0 && (
        <>
          <h3 className="mt-8 text-xs font-semibold uppercase tracking-wide text-gray-500">
            Points history
          </h3>
          <div className="mt-3 space-y-2">
            {summary.history.map((h, i) => (
              <div
                key={i}
                className="flex items-center justify-between rounded-xl border border-gray-100 bg-white px-4 py-2.5 text-sm"
              >
                <span className="text-gray-700">{h.service_name}</span>
                <span className="text-xs text-gray-400">
                  {new Date(h.date).toLocaleDateString()}
                </span>
                <span className="font-medium text-brand-700">+{h.points} pts</span>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
