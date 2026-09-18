import { DashboardData, ScenarioId } from "../types";

export class ApiClient {
  private static async fetchWithScenario(endpoint: string, scenario?: ScenarioId) {
    const url = new URL(endpoint, typeof window !== 'undefined' ? window.location.origin : 'http://localhost:3000');
    if (scenario) {
      url.searchParams.set("scenario", scenario);
    }
    const res = await fetch(url.toString(), {
      next: { revalidate: 0 },
      headers: { "Content-Type": "application/json" },
    });
    if (!res.ok) throw new Error(`API Error: ${res.statusText}`);
    return res.json();
  }

  static async getDashboard(scenario: ScenarioId = "normal"): Promise<DashboardData> {
    // Uses Next.js API route as a mock adapter
    return this.fetchWithScenario("/api/dashboard", scenario);
  }
}

