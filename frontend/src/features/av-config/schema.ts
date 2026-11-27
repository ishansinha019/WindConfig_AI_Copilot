import { z } from "zod";

import type { AvailabilitySnapshotDraft } from "@/lib/api";

export const basicDetailsSchema = z
  .object({
    name: z
      .string()
      .trim()
      .min(1, "Configuration name is required.")
      .max(160, "Name must be 160 characters or less."),
    calculation_type: z.string().nullable(),
    start_date: z.string().nullable(),
    end_date: z.string().nullable(),
  })
  .refine(
    (data) => {
      if (data.start_date && data.end_date) {
        return data.end_date > data.start_date;
      }
      return true;
    },
    {
      message: "End date must be after start date.",
      path: ["end_date"],
    },
  );

export const alarmAssignmentSchema = z.object({
  alarm_id: z.string(),
  turbine_ids: z.array(z.string()),
});

export const detailsSchema = z.object({
  park_availability_pct: z.number().nullable(),
  low_wind_variant: z.string().nullable(),
  high_wind_variant: z.string().nullable(),
});

export const availabilitySnapshotDraftSchema = z.object({
  schema_version: z.literal(2),
  basic_details: basicDetailsSchema,
  turbine_ids: z.array(z.string()),
  formula_code: z.string().nullable(),
  alarm_assignments: z.array(alarmAssignmentSchema),
  details: detailsSchema,
});

export type AvailabilitySnapshotFormValues = z.infer<typeof availabilitySnapshotDraftSchema>;

export function createEmptySnapshot(defaultParkAvailabilityPct?: number): AvailabilitySnapshotDraft {
  return {
    schema_version: 2,
    basic_details: {
      name: "",
      calculation_type: null,
      start_date: null,
      end_date: null,
    },
    turbine_ids: [],
    formula_code: null,
    alarm_assignments: [],
    details: {
      park_availability_pct: defaultParkAvailabilityPct ?? null,
      low_wind_variant: null,
      high_wind_variant: null,
    },
  };
}

export function normalizeSnapshot(
  raw: Record<string, unknown>,
  fallbackName: string,
  defaultParkAvailabilityPct?: number,
): AvailabilitySnapshotDraft {
  if (raw.schema_version === 2) {
    const basic = (raw.basic_details as Record<string, unknown> | undefined) ?? {};
    const details = (raw.details as Record<string, unknown> | undefined) ?? {};
    return {
      schema_version: 2,
      basic_details: {
        name: typeof basic.name === "string" && basic.name ? basic.name : fallbackName,
        calculation_type:
          typeof basic.calculation_type === "string" ? basic.calculation_type : null,
        start_date: typeof basic.start_date === "string" ? basic.start_date : null,
        end_date: typeof basic.end_date === "string" ? basic.end_date : null,
      },
      turbine_ids: Array.isArray(raw.turbine_ids) ? (raw.turbine_ids as string[]) : [],
      formula_code: typeof raw.formula_code === "string" ? raw.formula_code : null,
      alarm_assignments: Array.isArray(raw.alarm_assignments)
        ? (raw.alarm_assignments as Array<{ alarm_id: string; turbine_ids: string[] }>)
        : [],
      details: {
        park_availability_pct:
          typeof details.park_availability_pct === "number"
            ? details.park_availability_pct
            : (defaultParkAvailabilityPct ?? null),
        low_wind_variant:
          typeof details.low_wind_variant === "string" ? details.low_wind_variant : null,
        high_wind_variant:
          typeof details.high_wind_variant === "string" ? details.high_wind_variant : null,
      },
    };
  }

  // Fallback for legacy v1 snapshots
  return {
    schema_version: 2,
    basic_details: {
      name: fallbackName,
      calculation_type: "TBA",
      start_date: null,
      end_date: null,
    },
    turbine_ids: Array.isArray(raw.turbine_ids) ? (raw.turbine_ids as string[]) : [],
    formula_code: null,
    alarm_assignments: [],
    details: {
      park_availability_pct:
        typeof raw.target_availability === "number"
          ? raw.target_availability
          : (defaultParkAvailabilityPct ?? null),
      low_wind_variant: null,
      high_wind_variant: null,
    },
  };
}

export function isStepComplete(step: number, values: AvailabilitySnapshotDraft): boolean {
  switch (step) {
    case 1: {
      const b = values.basic_details;
      return Boolean(
        b.name.trim() &&
          b.calculation_type &&
          b.start_date &&
          b.end_date &&
          b.end_date > b.start_date,
      );
    }
    case 2:
      return values.turbine_ids.length > 0;
    case 3:
      return Boolean(values.formula_code && values.alarm_assignments.length > 0);
    case 4: {
      const d = values.details;
      return Boolean(
        d.park_availability_pct !== null &&
          d.park_availability_pct >= 0 &&
          d.park_availability_pct <= 100 &&
          d.low_wind_variant &&
          d.high_wind_variant,
      );
    }
    default:
      return false;
  }
}
