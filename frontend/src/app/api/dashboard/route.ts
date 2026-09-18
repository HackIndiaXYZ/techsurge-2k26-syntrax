import { NextRequest, NextResponse } from "next/server";
import { getScenarioData } from "@/lib/mock-data";
import { ScenarioId } from "@/lib/types";

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const scenarioParam = searchParams.get("scenario") as ScenarioId | null;
  const scenario = scenarioParam || "normal";

  const data = getScenarioData(scenario);
  return NextResponse.json(data);
}
