import LaunchIcon from '@mui/icons-material/Launch';
import { analytics } from '../config/firebase';
import { logEvent } from 'firebase/analytics';

const OverView = () => {

    const handleDownload = () => {
        logEvent(analytics, 'download_count');
    }
    
    const handleGitHubClick = () => {
        logEvent(analytics, 'github_repo_visit');

        window.open('https://github.com/Ashif4354/StreamStorm', '_blank');
    }

    return (
        <section id="overview" className="overview">
            <div className="overview-inner-container">
                <h2 className="tag-line">Unleash Chaos in <span className="red-text">YouTube Live Chats</span></h2>
                <span className="overview-description">
                    A desktop application to automate mass messaging. 
                    Storm chats in YouTube Live Streams at full throttle with zero efforts. 
                    No coding, no limits. Just Pure, unadulterated disruptions and chaos on command.
                </span>
                <div className="overview-buttons-container">
                    <a href="https://github.com/Ashif4354/StreamStorm/releases/latest/download/StreamStorm.Setup.exe" download>
                        <button className="overview-download-button" onClick={handleDownload}>
                            Download Now
                        </button>
                    </a>

                    <button className="overview-github-button" onClick={handleGitHubClick}>
                        View on GitHub &nbsp;&nbsp;<LaunchIcon />
                    </button>
                </div>
                <span className="download-note">
                    <i>For Windows 10+ | macOS & linux build coming soon...</i>
                </span>
                <span className="download-note">
                    Safe to install. No background monitoring. No data collected. Fully open source.
                </span>
                <div className="overview-image-container">
                    <img src="assets/ss.png" alt="StreamStorm Overview" className="overview-media" />
                </div>
            </div>
        </section>
    );
};

export default OverView;
