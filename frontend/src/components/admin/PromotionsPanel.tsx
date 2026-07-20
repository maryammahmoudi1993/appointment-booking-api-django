import { useEffect, useState } from "react";
import {
  promotionsApi,
  servicesApi,
  type PromoCode,
  type Service,
} from "../../api/client";

function extractErrorMessage(err: any, fallback: string): string {
  const data = err.response?.data;
  if (!data) return fallback;
  const firstFieldError = Object.values(data).flat()[0];
  return typeof firstFieldError === "string" ? firstFieldError : fallback;
}

const EMPTY_FORM = {
  code: "",
  description: "",
  discount_type: "percent" as "percent" | "fixed",
  discount_value: "",
};

export default function PromotionsPanel() {
  const [promos, setPromos] = useState<PromoCode[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const [serviceIds, setServiceIds] = useState<number[]>([]);
  const [error, setError] = useState("");

  const fetchAll = () => {
    setLoading(true);
    Promise.all([promotionsApi.list(), servicesApi.list()])
      .then(([promoRes, servicesRes]) => {
        setPromos(promoRes.data.results);
        setServices(servicesRes.data.results);
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchAll();
  }, []);

  const toggleService = (id: number) => {
    setServiceIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await promotionsApi.create({ ...form, services: serviceIds });
      setForm(EMPTY_FORM);
      setServiceIds([]);
      setShowForm(false);
      fetchAll();
    } catch (err: any) {
      setError(extractErrorMessage(err, "Failed to create promo code."));
    }
  };

  const toggleActive = async (promo: PromoCode) => {
    await promotionsApi.update(promo.id, { is_active: !promo.is_active });
    fetchAll();
  };

  if (loading) {
    return (
      <div className="flex justify-center py-10">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-brand-500 border-t-transparent" />
      </div>
    );
  }

  const liveCampaigns = promos.filter((p) => p.is_active).length;
  const totalRedemptions = promos.reduce((sum, p) => sum + p.times_redeemed, 0);
  const revenueInfluenced = promos.reduce(
    (sum, p) => sum + Number(p.revenue_influenced),
    0
  );

  return (
    <div>
      <div className="mb-6 grid gap-4 sm:grid-cols-3">
        <div className="rounded-2xl bg-brand-50 p-5 text-brand-800">
          <p className="text-xs font-medium uppercase tracking-wide opacity-70">
            Live campaigns
          </p>
          <p className="mt-1 font-display text-3xl font-bold">{liveCampaigns}</p>
        </div>
        <div className="rounded-2xl bg-gray-50 p-5 text-gray-800">
          <p className="text-xs font-medium uppercase tracking-wide opacity-70">
            Total redemptions
          </p>
          <p className="mt-1 font-display text-3xl font-bold">{totalRedemptions}</p>
        </div>
        <div className="rounded-2xl bg-brand-50 p-5 text-brand-800">
          <p className="text-xs font-medium uppercase tracking-wide opacity-70">
            Est. revenue influenced
          </p>
          <p className="mt-1 font-display text-3xl font-bold">
            ${revenueInfluenced.toFixed(0)}
          </p>
        </div>
      </div>

      <button
        onClick={() => setShowForm((v) => !v)}
        className="mb-4 rounded-full bg-brand-600 px-5 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700"
      >
        {showForm ? "Cancel" : "+ New campaign"}
      </button>

      {showForm && (
        <form
          onSubmit={handleCreate}
          className="mb-6 rounded-2xl border border-brand-100 bg-white p-6 shadow-sm"
        >
          {error && (
            <p className="mb-3 rounded-lg bg-red-50 p-2 text-xs text-red-700">
              {error}
            </p>
          )}
          <div className="grid gap-3 sm:grid-cols-2">
            <input
              placeholder="Code (e.g. WELCOME15)"
              value={form.code}
              onChange={(e) => setForm({ ...form, code: e.target.value })}
              required
              className="rounded-lg border border-gray-300 px-3 py-2 text-sm uppercase focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
            <input
              placeholder="Description"
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
            <select
              value={form.discount_type}
              onChange={(e) =>
                setForm({ ...form, discount_type: e.target.value as "percent" | "fixed" })
              }
              className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            >
              <option value="percent">Percent off</option>
              <option value="fixed">Fixed amount off</option>
            </select>
            <input
              placeholder={form.discount_type === "percent" ? "15" : "20.00"}
              type="number"
              step="0.01"
              value={form.discount_value}
              onChange={(e) => setForm({ ...form, discount_value: e.target.value })}
              required
              className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>

          <div className="mt-4">
            <p className="text-sm font-medium text-gray-700">Applies to</p>
            <p className="text-xs text-gray-400">
              Leave all unchecked to apply this code to every service.
            </p>
            <div className="mt-2 flex flex-wrap gap-2">
              {services.map((sv) => (
                <label
                  key={sv.id}
                  className={`cursor-pointer rounded-full border px-3 py-1 text-xs font-medium transition ${
                    serviceIds.includes(sv.id)
                      ? "border-brand-600 bg-brand-50 text-brand-700"
                      : "border-gray-200 text-gray-600 hover:border-brand-300"
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={serviceIds.includes(sv.id)}
                    onChange={() => toggleService(sv.id)}
                    className="mr-1.5 hidden"
                  />
                  {sv.name}
                </label>
              ))}
            </div>
          </div>

          <button
            type="submit"
            className="mt-5 rounded-full bg-brand-600 px-5 py-2 text-sm font-semibold text-white hover:bg-brand-700"
          >
            Create campaign
          </button>
        </form>
      )}

      <div className="overflow-x-auto rounded-2xl border border-brand-100 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-gray-100 text-sm">
          <thead>
            <tr className="text-left text-xs font-medium uppercase tracking-wide text-gray-500">
              <th className="px-4 py-3">Promotion</th>
              <th className="px-4 py-3">Code</th>
              <th className="px-4 py-3">Discount</th>
              <th className="px-4 py-3">Applies to</th>
              <th className="px-4 py-3">Redemptions</th>
              <th className="px-4 py-3">Active</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {promos.map((p) => (
              <tr key={p.id}>
                <td className="px-4 py-3 text-gray-700">{p.description || "—"}</td>
                <td className="px-4 py-3">
                  <code className="rounded bg-gray-100 px-2 py-0.5 text-xs font-semibold">
                    {p.code}
                  </code>
                </td>
                <td className="px-4 py-3 text-gray-700">
                  {p.discount_type === "percent"
                    ? `${p.discount_value}% off`
                    : `$${p.discount_value} off`}
                </td>
                <td className="px-4 py-3 text-xs text-gray-600">
                  {p.service_names.length === 0
                    ? "All services"
                    : p.service_names.join(", ")}
                </td>
                <td className="px-4 py-3 text-gray-700">{p.times_redeemed}</td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => toggleActive(p)}
                    className={`relative h-6 w-11 rounded-full transition ${
                      p.is_active ? "bg-brand-600" : "bg-gray-200"
                    }`}
                  >
                    <span
                      className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition ${
                        p.is_active ? "left-5" : "left-0.5"
                      }`}
                    />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {promos.length === 0 && (
          <p className="p-6 text-center text-sm text-gray-500">
            No campaigns yet — create one above.
          </p>
        )}
      </div>
    </div>
  );
}
