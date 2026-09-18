import { NextRequest, NextResponse } from "next/server";
import { getScenarioData } from "@/lib/mock-data";
import type { ScenarioId } from "@/lib/types";

const VALID_SCENARIOS: ScenarioId[] = [
  "normal",
  "corrupted-source",
  "no-consensus",
  "duplicate-settlement",
];

/**
 * GET /api/dashboard?scenario=normal
 *
 * Returns deterministic mock data for the requested scenario.
 * When the real FastAPI backend is available, this route will
 * proxy to GET /v1/dashboard instead.
 */
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const scenario = (searchParams.get("scenario") || "normal") as ScenarioId;

  if (!VALID_SCENARIOS.includes(scenario)) {
    return NextResponse.json(
      { code: "INVALID_SCENARIO", message: `Unknown scenario: ${scenario}`, correlation_id: null },
      { status: 400 }
    );
  }

  const data = getScenarioData(scenario);
  return NextResponse.json(data);
}
