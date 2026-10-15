import createClient from "openapi-fetch";
import type { paths, components } from "./schema";
export const api = createClient<paths>({ baseUrl: "" });
export type Dashboard = components["schemas"]["Dashboard"];
export type Indicator = components["schemas"]["Indicator"];
export type Sector = components["schemas"]["Sector"];
export type Relationship = components["schemas"]["Relationship"];
export type Point = components["schemas"]["Point"];
