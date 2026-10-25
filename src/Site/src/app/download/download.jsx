"use client";

import { useEffect, useState } from 'react';
import { logEvent } from 'firebase/analytics';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';

import { analytics } from '@/config/firebase';
import * as atatus from '@/config/atatus';
import Windows from './sections/windows';
import Linux from './sections/linux';
import Mac from './sections/mac';

const OS_NAMES = ['windows', 'linux', 'mac'];

const DownloadPage = () => {

    const [tabValue, setTabValue] = useState(0);

    const handleTabChange = (event, newValue) => {
        setTabValue(newValue);
        const selectedOs = OS_NAMES[newValue] || 'unknown';
        atatus.addAction('download-os-tab-selected', { os: selectedOs });
        atatus.addFeatureFlagEvaluation('selected_os_tab', selectedOs);
        atatus.setViewContextProperty('selectedOs', selectedOs);
        atatus.downloadLogger.info(`Switched download OS tab to ${selectedOs}`);
    };

    useEffect(() => {
        logEvent(analytics, 'download_page_viewed', {
            page_location: window.location.href,
            page_path: window.location.pathname,
            page_title: document.title
        });
        atatus.addFeatureFlagEvaluation('selected_os_tab', OS_NAMES[0]);
        atatus.setViewContextProperty('selectedOs', OS_NAMES[0]);
        atatus.downloadLogger.info('Download page viewed');
    }, []);

    return (
        <div className='download-page'>
            <article className='download-container'>
                <h1 className='download-title'>Download and install StreamStorm</h1>
                <span className='download-description'>By using StreamStorm, you agree to our <a href='/tc'>Terms of Service</a> and <a href='/pp'>Privacy Policy</a>.</span>
                <span className='download-description'>Select your operating system</span>
                <Tabs value={tabValue} onChange={handleTabChange} centered>
                    <Tab label="Windows" data-atatus-action-name="tab-download-windows" />
                    <Tab label="Linux" data-atatus-action-name="tab-download-linux" />
                    <Tab label="Mac" data-atatus-action-name="tab-download-mac" />
                </Tabs>
                <div className='download-sections'>
                    {
                        tabValue === 0 ? (
                            <Windows />
                        ) : tabValue === 1 ? (
                            <Linux />
                        ) : (
                            <Mac />
                        )
                    }
                </div>

            </article>

        </div>
    );
};

export default DownloadPage;
