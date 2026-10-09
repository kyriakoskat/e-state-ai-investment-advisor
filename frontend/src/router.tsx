import {
  createRouter, createRootRoute, createRoute, Outlet,
} from "@tanstack/react-router";

import { Dashboard } from "./pages/Dashboard";
import { PlotPage } from "./pages/PlotPage";

const rootRoute = createRootRoute({ component: () => <Outlet /> });

const dashboardRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  component: Dashboard,
});

const plotRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/plots/$plotId",
  component: PlotPage,
});

const routeTree = rootRoute.addChildren([dashboardRoute, plotRoute]);

export const router = createRouter({ routeTree });

declare module "@tanstack/react-router" {
  interface Register { router: typeof router; }
}
