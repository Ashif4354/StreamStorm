import EachFeature from "./EachFeature";

import GroupsOutlinedIcon from '@mui/icons-material/GroupsOutlined';
import AccessTimeOutlinedIcon from '@mui/icons-material/AccessTimeOutlined';
import SettingsOutlinedIcon from '@mui/icons-material/SettingsOutlined';
import AccessibilityNewOutlinedIcon from '@mui/icons-material/AccessibilityNewOutlined';
import LockOpenOutlinedIcon from '@mui/icons-material/LockOpenOutlined';
import AnalyticsOutlinedIcon from '@mui/icons-material/AnalyticsOutlined';
import StyleOutlinedIcon from '@mui/icons-material/StyleOutlined';
import AccountBoxOutlinedIcon from '@mui/icons-material/AccountBoxOutlined';
import OndemandVideoIcon from '@mui/icons-material/OndemandVideo';

const FEATURES = [
    {
        title: "Multi-Account Management",
        description: "Operate multiple YouTube channels in separate, isolated browser profiles to avoid detection.",
        icon: <GroupsOutlinedIcon sx={{ fontSize: '2rem', color: 'var(--light-red)' }} />,
    },
    {
        title: "Custom Channel Creation",
        description: "Create channels with custom names, and logos",
        icon: <OndemandVideoIcon sx={{ fontSize: '2rem', color: 'var(--light-red)' }} />,
    },
    {
        title: "Custom Message Scheduling",
        description: "Control timing with flexible intervals, supporting both rapid-fire spam and strategic, delayed delivery.",
        icon: <AccessTimeOutlinedIcon sx={{ fontSize: '2rem', color: 'var(--light-red)' }} />,
    },
    {
        title: "Advanced Tuning",
        description: "Fine-tune performance parameters like slow-mode delays and headless browsing to match your system limits.",
        icon: <SettingsOutlinedIcon sx={{ fontSize: '2rem', color: 'var(--light-red)' }} />,
    },
    {
        title: "User-Friendly Interface",
        description: "Intuitive design with a dashboard for easy management of the storm.",
        icon: <AccessibilityNewOutlinedIcon sx={{ fontSize: '2rem', color: 'var(--light-red)' }} />,
    },
    {
        title: "In-App System Monitoring",
        description: "Real-time RAM tracking ensures system stability and dynamically calculates how many channels can be run.",
        icon: <AnalyticsOutlinedIcon sx={{ fontSize: '2rem', color: 'var(--light-red)' }} />,
    },
    {
        title: "Flexible Channel Selection",
        description: "Choose a fixed number of channels, a range (e.g., 5-15), or manually pick specific channels to storm.",
        icon: <StyleOutlinedIcon sx={{ fontSize: '2rem', color: 'var(--light-red)' }} />,
    },
    {
        title: "One-Click Profile System",
        description: "Automatically generate, configure, and clean up temporary browser profiles to prevent data collision.",
        icon: <AccountBoxOutlinedIcon sx={{ fontSize: '2rem', color: 'var(--light-red)' }} />,
    },
    {
        title: "Open Source",
        description: "Fully transparent codebase, allowing you to inspect, modify, and contribute to the project.",
        icon: <LockOpenOutlinedIcon sx={{ fontSize: '2rem', color: 'var(--light-red)' }} />,
    },
    
]

const Features = () => {
    return (
        <section className="features" id="features">
            <div className="features-inner-container">
                <h2 className="features-heading">Built for Maximum Impact</h2>
                <span className="features-description">
                    Core functionality designed for efficiency and power.
                </span>
                <div className="features-list">
                    {
                        FEATURES.map((feature, index) => (
                            <EachFeature
                                key={index}
                                title={feature.title}
                                description={feature.description}
                                icon={feature.icon}
                            />
                        ))
                    }
                </div>
            </div>
        </section>
    );
};

export default Features;