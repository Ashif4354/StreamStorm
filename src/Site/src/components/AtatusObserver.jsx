"use client";

import { useEffect, useRef } from "react";
import { usePathname, useSearchParams } from "next/navigation";
import * as atatus from "../config/atatus";

export default function AtatusObserver() {
    const pathname = usePathname();
    const searchParams = useSearchParams();
    const isFirstRun = useRef(true);

    useEffect(() => {
        atatus.installGlobalObservers();
    }, []);

    useEffect(() => {
        if (!pathname) return;

        const search = searchParams ? searchParams.toString() : "";
        const fullPath = search ? `${pathname}?${search}` : pathname;

        atatus.setViewName(pathname);
        atatus.setViewContext({
            pathname,
            search,
            fullPath,
            referrer: typeof document !== "undefined" ? document.referrer : "",
        });

        if (isFirstRun.current) {
            isFirstRun.current = false;
            if (typeof performance !== "undefined" && typeof performance.now === "function") {
                atatus.setViewLoadingTime(Math.round(performance.now()));
            }
            atatus.navLogger.info("Initial page load", { pathname, fullPath });
        } else {
            atatus.navLogger.info("Client-side route changed", { pathname, fullPath });
            atatus.addAction("route-changed", { to: pathname });
        }
    }, [pathname, searchParams]);

    return null;
}
