/**
 * Deterministic check of the reporter's tariff against Octopus Energy's public products API - the
 * same check the maintainer does by hand for "unknown product" and "no rates" reports (#1452,
 * #1432, #1417, #1499). Tariff codes aren't personal data and the API needs no key.
 */

const PRODUCTS_API = 'https://api.octopus.energy/v1/products';
const REQUEST_TIMEOUT_MS = 10_000;
const MAX_TARIFFS = 2;
const DAY_MS = 24 * 60 * 60 * 1000;

// Same shape as the integration's REGEX_TARIFF_PARTS (const.py), but requiring the energy/rate prefix
// so serials or other codes typed into the field aren't mistaken for tariffs.
const TARIFF_CODE = /(?<![A-Z0-9-])([EG])-([0-9A-Z]+)-([A-Z0-9][A-Z0-9-]*)-([A-Z])(?![A-Z0-9-])/g;

export type TariffProblem = 'product_not_found' | 'no_rates';

export interface TariffCheck {
  /** Verified facts for the analysis/critic, one "- ..." line each. */
  facts: string[];
  problems: TariffProblem[];
  gates: string[];
}

async function getJson(url: string): Promise<{ status: number; body: any }> {
  const response = await fetch(url, { signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS), headers: { Accept: 'application/json' } });
  return { status: response.status, body: response.ok ? await response.json() : null };
}

/** Tariff codes in the reporter's Tariff Code field, e.g. "E-1R-INTELLI-VAR-22-10-14-A". */
export function parseTariffCodes(text: string): Array<{ code: string; energy: 'E' | 'G'; rate: string; product: string }> {
  const found = Array.from((text ?? '').toUpperCase().matchAll(TARIFF_CODE), (m) => ({ code: m[0], energy: m[1] as 'E' | 'G', rate: m[2], product: m[3] }));
  return found.filter((t, i) => found.findIndex((o) => o.code === t.code) === i).slice(0, MAX_TARIFFS);
}

/**
 * Tariff codes from agreements in attached diagnostics that were active at `at` - diagnostics list
 * past agreements too, and an expired tariff would wrongly look like "no rates" (same rule as the
 * integration's get_active_tariff). For when the form field just says "see above" (#1948).
 */
export function activeTariffsFromDiagnostics(text: string, at: string | undefined): string[] {
  const when = at ? new Date(at).getTime() : Date.now();
  const agreement = /"start"\s*:\s*"([^"]+)"\s*,\s*"end"\s*:\s*(null|"[^"]*")\s*,\s*"tariff_code"\s*:\s*"([^"]+)"/g;
  return Array.from((text ?? '').matchAll(agreement))
    .filter((m) => {
      const start = Date.parse(m[1]);
      const end = m[2] === 'null' ? null : Date.parse(m[2].replace(/"/g, ''));
      return !Number.isNaN(start) && start <= when && (end === null || Number.isNaN(end) || end >= when);
    })
    .map((m) => m[3]);
}

/** Checks each tariff: does the product exist, and are unit rates published around `at`? */
export async function checkTariffs(tariffField: string, at: string | undefined): Promise<TariffCheck> {
  const result: TariffCheck = { facts: [], problems: [], gates: [] };
  const when = at ? new Date(at) : new Date();
  const from = new Date(when.getTime() - DAY_MS).toISOString().replace(/\.\d+Z$/, 'Z');
  const to = new Date(when.getTime() + DAY_MS).toISOString().replace(/\.\d+Z$/, 'Z');

  for (const tariff of parseTariffCodes(tariffField)) {
    try {
      const product = await getJson(`${PRODUCTS_API}/${tariff.product}/`);
      if (product.status === 404) {
        result.problems.push('product_not_found');
        result.facts.push(`- Octopus Energy's public API has no product "${tariff.product}" (from tariff ${tariff.code}).`);
        continue;
      }
      if (product.status !== 200) {
        result.gates.push(`tariff: product lookup for ${tariff.product} returned ${product.status}`);
        continue;
      }

      const tariffs = tariff.energy === 'G' ? 'gas-tariffs' : 'electricity-tariffs';
      // Economy 7 style (2R) tariffs publish day/night rates instead of standard ones.
      const rates = tariff.energy === 'E' && tariff.rate.includes('2') ? 'day-unit-rates' : 'standard-unit-rates';
      const response = await getJson(`${PRODUCTS_API}/${tariff.product}/${tariffs}/${tariff.code}/${rates}/?period_from=${from}&period_to=${to}`);
      if (response.status !== 200) {
        result.gates.push(`tariff: rates lookup for ${tariff.code} returned ${response.status}`);
        continue;
      }
      const count = Number(response.body?.count ?? response.body?.results?.length ?? 0);
      if (count === 0) {
        result.problems.push('no_rates');
        result.facts.push(`- Octopus Energy's public API returned no unit rates for tariff ${tariff.code} between ${from} and ${to} (around when the issue was opened).`);
      } else {
        result.facts.push(`- Octopus Energy's public API returned ${count} unit rate(s) for tariff ${tariff.code} between ${from} and ${to}, so its rates were published.`);
      }
    } catch (error) {
      result.gates.push(`tariff: check for ${tariff.code} failed (${(error as Error).message})`);
    }
  }
  return result;
}
