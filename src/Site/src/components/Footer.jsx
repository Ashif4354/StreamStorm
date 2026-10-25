"use client"
import { useVisitCount } from "@/context/VisitCountContext";
import * as atatus from "@/config/atatus";

const Footer = () => {
    const visitCount = useVisitCount();

    const handleFooterLinkClick = (link) => {
        atatus.addAction('site-footer-link-clicked', { link });
        atatus.navLogger.info(`Site footer link clicked: ${link}`, { link });
    };

    return (
        <footer className="footer">
            <div className="footer-elements">
                <a
                    href="/tc"
                    className="footer-element"
                    onClick={() => handleFooterLinkClick('tc')}
                    data-atatus-action-name="footer-terms-and-conditions"
                >
                    Terms and Conditions
                </a>
                <a
                    href="/pp"
                    className="footer-element"
                    onClick={() => handleFooterLinkClick('pp')}
                    data-atatus-action-name="footer-privacy-policy"
                >
                    Privacy Policy
                </a>
                {visitCount && <span className="footer-element">Visit Count: {visitCount}</span>}
            </div>
            <br />
            © {new Date().getFullYear()} StreamStorm. All rights reserved.
        </footer>
    );
};

export default Footer;
