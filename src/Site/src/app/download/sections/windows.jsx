import { useDownloadCount } from "@/context/DownloadCountContext";
import { useState } from "react";
import { safeLogEvent as logEvent } from '../../../config/safeAnalytics.js';
import { analytics } from "@/config/firebase";
import * as atatus from "@/config/atatus";

const Windows = () => {

    const [downloadButtonDisabled, setDownloadButtonDisabled] = useState(false);

    const { downloadCount, updateDownloadCount } = useDownloadCount();

    const handleDownload = () => {
        setDownloadButtonDisabled(true);
        atatus.addAction('download-windows-installer-clicked');
        atatus.downloadLogger.info('Windows installer download initiated');
        logEvent(analytics, 'download_count');
        updateDownloadCount();

        setTimeout(() => {
            setDownloadButtonDisabled(false);
        }, 5000); // Reset button after 5 seconds
    };

    return (
        <section className='download-section'>
            <div className='download-section-title-container'>
                <h4 className='download-section-title'>Download for Windows</h4>
            </div>
            <span className="download-note">
                <i>For Windows 10+</i>
            </span>

            <div className='windows-download-container'>
                <div className='windows-icon'>🪟</div>
                <p className='windows-description'>
                    Download the StreamStorm installer and get started in minutes.
                </p>
                <a
                    href="https://github.com/Ashif4354/StreamStorm/releases/latest/download/StreamStorm.Setup.exe"
                    className="download-anchor"
                    download
                    data-atatus-action-name="link-download-windows-installer"
                >
                    <button
                        className="windows-download-button"
                        onClick={handleDownload}
                        disabled={downloadButtonDisabled}
                        data-atatus-action-name="btn-download-windows-exe"
                    >
                        {downloadButtonDisabled ? 'Downloading...' : '↓ Download Now'}
                    </button>
                </a>
                {
                    downloadCount && (
                        <span className="windows-download-count">
                            <i>Total Downloads: {downloadCount}</i>
                        </span>
                    )
                }
            </div>
        </section>
    );
};

export default Windows;
