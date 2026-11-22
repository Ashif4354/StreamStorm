"use client";

import { useEffect, useRef } from "react";
import { usePathname } from "next/navigation";
import * as atatus from "../config/atatus";

export default function AtatusObserver() {
    const pathname = usePathname();
    const isFirstRun = useRef(true);

    useEffect(() => {
        atatus.installGlobalObservers();
    }, []);

    useEffect(() => {
        if (!pathname) return;

        let referrerOrigin = "";
        try {
            referrerOrigin = typeof document !== "undefined" && document.referrer ? new URL(document.referrer).origin : "";
        } catch (_) {}

        atatus.setViewName(pathname);
        atatus.setViewContext({
            pathname,
            referrer: referrerOrigin,
        });

        if (isFirstRun.current) {
            isFirstRun.current = false;
            if (typeof performance !== "undefined" && typeof performance.now === "function") {
                atatus.setViewLoadingTime(Math.round(performance.now()));
            }
            atatus.navLogger.info("Initial page load", { pathname });
        } else {
            atatus.navLogger.info("Client-side route changed", { pathname });
            atatus.addAction("route-changed", { to: pathname });
        }
    }, [pathname]);

    return null;
}
